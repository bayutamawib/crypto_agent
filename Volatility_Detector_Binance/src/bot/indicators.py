import pandas as pd
import numpy as np
from ta.volatility import AverageTrueRange, BollingerBands
from ta.trend import SMAIndicator
from ta.momentum import StochasticOscillator
from .binance_api import get_binance_client, get_klines_from_binance
from .logger import get_logger
from .config import STOCH_K_PERIOD, STOCH_K_SMOOTHING, SMA_PERIODS, ATR_PERIOD, BB_PERIOD

logger = get_logger(__name__)

def get_historical_data_for_symbol(symbol: str, interval: str = "1m", limit: int = 100) -> pd.DataFrame:
    """
    Fetches historical OHLCV data for a given cryptocurrency symbol from Binance API.

    Args:
        symbol (str): The cryptocurrency symbol (e.g., BTCUSDT).
        interval (str): The candlestick interval (1m, 5m, 15m, 1h, 4h, 1d, etc.).
        limit (int): The number of candlesticks to fetch (max 1000).

    Returns:
        pd.DataFrame: A DataFrame with OHLCV data.
    """
    try:
        binance_client = get_binance_client()
        if binance_client is None:
            logger.warning(f"Could not initialize Binance client for {symbol}, generating mock data")
            return get_mock_historical_data(symbol, limit)
        
        historical_data = get_klines_from_binance(binance_client, symbol, interval, limit)
        
        if historical_data.empty:
            logger.warning(f"No historical data for {symbol}, generating mock data")
            return get_mock_historical_data(symbol, limit)
        
        return historical_data
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return get_mock_historical_data(symbol, limit)

def get_mock_historical_data(symbol: str, limit: int = 100) -> pd.DataFrame:
    """
    Generates mock historical OHLCV data for testing purposes.

    Args:
        symbol (str): The cryptocurrency symbol.
        limit (int): The number of data points to generate.

    Returns:
        pd.DataFrame: A DataFrame with mock historical data.
    """
    dates = pd.to_datetime(pd.date_range(end=pd.Timestamp.now(), periods=limit, freq='1min'))
    # Start with a random price and let it fluctuate
    price = np.random.uniform(low=100, high=50000)
    prices = [price]
    for _ in range(1, limit):
        price += np.random.uniform(low=-2, high=2)
        prices.append(price)
    prices = np.array(prices)
    
    high = prices + np.random.uniform(low=0, high=2, size=limit)
    low = prices - np.random.uniform(low=0, high=2, size=limit)
    open_ = prices + np.random.uniform(low=-1, high=1, size=limit)
    volume = np.random.randint(low=100000, high=1000000, size=limit)
    
    return pd.DataFrame({
        'Date': dates,
        'Open': open_,
        'High': high,
        'Low': low,
        'Close': prices,
        'Volume': volume
    })

def calculate_stoch_k(df: pd.DataFrame, period: int = 14, smoothing: int = 3) -> float:
    """
    Calculates the Stochastic K indicator.
    
    Args:
        df (pd.DataFrame): Historical OHLCV data.
        period (int): The period for Stochastic calculation (default 14).
        smoothing (int): The smoothing period (default 3).
    
    Returns:
        float: The current Stochastic K value.
    """
    try:
        stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], 
                                     window=period, smooth_window=smoothing)
        stoch_k = stoch.stoch().iloc[-1]
        return stoch_k if not pd.isna(stoch_k) else 0.0
    except Exception as e:
        logger.warning(f"Error calculating Stoch_K: {e}")
        return 0.0

def calculate_sma_from_1min_data(symbol: str, limit: int = 100) -> dict:
    """
    Fetches 1-minute candle data and calculates SMA indicators.

    Args:
        symbol (str): The cryptocurrency symbol (e.g., BTCUSDT).
        limit (int): The number of 1-minute candles to fetch.

    Returns:
        dict: Dictionary with sma_9, sma_12, sma_26 calculated from 1-minute data.
    """
    sma_indicators = {}
    try:
        # Fetch 1-minute candles for SMA calculation
        df_1min = get_historical_data_for_symbol(symbol, interval="1m", limit=limit)

        if df_1min.empty or len(df_1min) < 26:
            logger.warning(f"Not enough 1-minute data for {symbol} to calculate SMA")
            return sma_indicators

        # Calculate SMA from 1-minute data
        for period in SMA_PERIODS:
            sma = SMAIndicator(close=df_1min['Close'], window=period)
            sma_indicators[f'sma_{period}'] = sma.sma_indicator().iloc[-1]

    except Exception as e:
        logger.warning(f"Error calculating SMA from 1-minute data for {symbol}: {e}")

    return sma_indicators

def calculate_indicators(df: pd.DataFrame, symbol: str = None) -> dict:
    """
    Calculates all the required technical indicators for a given DataFrame.
    SMA indicators are calculated from 1-minute candle data.

    Args:
        df (pd.DataFrame): The input DataFrame with historical OHLCV data (1-minute).
        symbol (str): The cryptocurrency symbol for fetching 1-minute SMA data.

    Returns:
        dict: A dictionary containing the calculated indicators.
    """
    indicators = {}

    try:
        # ATR (14) - from 1-minute data
        atr_indicator = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=ATR_PERIOD)
        indicators['atr_14'] = atr_indicator.average_true_range().iloc[-1]

        # SMA (9, 12, 26) - from 1-minute data
        if symbol:
            sma_1min = calculate_sma_from_1min_data(symbol, limit=100)
            indicators.update(sma_1min)
        else:
            # Fallback to 1-minute data if symbol not provided
            for period in SMA_PERIODS:
                sma = SMAIndicator(close=df['Close'], window=period)
                indicators[f'sma_{period}'] = sma.sma_indicator().iloc[-1]
        
        # Bollinger Bands (20) - from 1-minute data
        bb_indicator = BollingerBands(close=df['Close'], window=BB_PERIOD)
        indicators['bb_high'] = bb_indicator.bollinger_hband().iloc[-1]
        indicators['bb_low'] = bb_indicator.bollinger_lband().iloc[-1]
        indicators['bb_ma'] = bb_indicator.bollinger_mavg().iloc[-1]

        # Stochastic K (7, smoothing 3) - from 1-minute data
        indicators['stoch_k_14'] = calculate_stoch_k(df, STOCH_K_PERIOD, STOCH_K_SMOOTHING)
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
    
    return indicators

if __name__ == '__main__':
    # This part is for testing the functions in this file.
    symbol = "BTCUSDT"
    historical_data = get_historical_data_for_symbol(symbol)
    
    if not historical_data.empty and len(historical_data) >= 26:
        print(f"Historical Data for {symbol}:")
        print(historical_data.head())
        print("...")
        print(historical_data.tail())

        indicators = calculate_indicators(historical_data)
        
        print("\nCalculated Indicators:")
        for key, value in indicators.items():
            print(f"{key}: {value:.2f}")
    else:
        print("Not enough data to calculate indicators.")
