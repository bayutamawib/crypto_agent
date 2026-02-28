"""
Single Ticker Analysis Module
Provides detailed technical analysis for a specific cryptocurrency ticker
"""

from .binance_api import get_binance_client, get_klines_from_binance
from .indicators import calculate_indicators
from .logger import get_logger
import pandas as pd

logger = get_logger(__name__)

def get_ticker_current_data(symbol: str):
    """
    Fetches current market data for a specific ticker.
    
    Args:
        symbol (str): Ticker symbol (e.g., BTCUSDT)
    
    Returns:
        dict: Current ticker data or None if not found
    """
    try:
        logger.info(f"Fetching current data for {symbol}...")
        binance_client = get_binance_client()
        if binance_client is None:
            logger.error("Failed to initialize Binance client")
            return None
        
        # Get 24hr ticker stats
        stats = binance_client.get_ticker(symbol=symbol)
        
        if not stats:
            logger.error(f"Ticker {symbol} not found")
            return None
        
        return {
            'symbol': symbol,
            'lastPrice': float(stats.get('lastPrice', 0)),
            'price24hPcnt': float(stats.get('priceChangePercent', 0)),
            'turnover24h': float(stats.get('volume', 0)),  # Use volume instead
            'volume24h': float(stats.get('volume', 0)),
            'markPrice': float(stats.get('lastPrice', 0)),
            'indexPrice': float(stats.get('lastPrice', 0)),
        }
    
    except Exception as e:
        logger.error(f"Error fetching ticker data: {e}")
        return None

def get_ticker_historical_data(symbol: str, interval: str = "1m", limit: int = 200):
    """
    Fetches historical OHLCV data for a specific ticker.
    
    Args:
        symbol (str): Ticker symbol (e.g., BTCUSDT)
        interval (str): Candlestick interval (1m, 5m, 15m, 1h, etc.)
        limit (int): Number of candles to fetch
    
    Returns:
        pd.DataFrame: Historical OHLCV data
    """
    try:
        logger.info(f"Fetching historical data for {symbol}...")
        binance_client = get_binance_client()
        if binance_client is None:
            logger.error("Failed to initialize Binance client")
            return pd.DataFrame()
        
        klines = get_klines_from_binance(binance_client, symbol, interval, limit)
        return klines
    
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()

def calculate_price_changes(historical_data: pd.DataFrame):
    """
    Calculates price changes over different timeframes.
    
    Args:
        historical_data (pd.DataFrame): Historical OHLCV data
    
    Returns:
        dict: Price changes for different timeframes
    """
    if historical_data.empty or len(historical_data) < 2:
        return {}
    
    current_price = historical_data.iloc[-1]['Close']
    
    changes = {}
    
    # Calculate changes for different timeframes
    timeframes = {
        '5_min': 5,
        '15_min': 15,
        '30_min': 30,
        '1_hour': 60,
        '2_hour': 120,
        '4_hour': 240,
    }
    
    for name, minutes in timeframes.items():
        if len(historical_data) >= minutes:
            old_price = historical_data.iloc[-minutes]['Close']
            change = ((current_price - old_price) / old_price) * 100
            changes[name] = change
        else:
            changes[name] = None
    
    return changes

def analyze_single_ticker(symbol: str, interval: str = "1m", limit: int = 200):
    """
    Performs comprehensive analysis on a single ticker.
    
    Args:
        symbol (str): Ticker symbol (e.g., BTCUSDT)
        interval (str): Candlestick interval for historical data
        limit (int): Number of candles to fetch
    
    Returns:
        dict: Complete analysis results
    """
    logger.info("="*100)
    logger.info(f"SINGLE TICKER ANALYSIS: {symbol}")
    logger.info("="*100)
    
    # Get current data
    current_data = get_ticker_current_data(symbol)
    if current_data is None:
        logger.error(f"Failed to get current data for {symbol}")
        return None
    
    # Get historical data
    historical_data = get_ticker_historical_data(symbol, interval, limit)
    if historical_data.empty:
        logger.error(f"Failed to get historical data for {symbol}")
        return None
    
    # Calculate indicators
    indicators = {}
    if len(historical_data) >= 26:
        logger.info("Calculating technical indicators...")
        indicators = calculate_indicators(historical_data, symbol=symbol)
    else:
        logger.warning(f"Not enough data for indicators: {len(historical_data)} < 26")
    
    # Calculate price changes
    price_changes = calculate_price_changes(historical_data)
    
    # Compile results
    results = {
        'symbol': symbol,
        'current_data': current_data,
        'historical_data': historical_data,
        'indicators': indicators,
        'price_changes': price_changes,
        'data_points': len(historical_data)
    }
    
    return results

def display_single_ticker_analysis(results: dict):
    """
    Displays comprehensive analysis for a single ticker.
    
    Args:
        results (dict): Analysis results from analyze_single_ticker()
    """
    if results is None:
        logger.error("No results to display")
        return
    
    symbol = results['symbol']
    current_data = results['current_data']
    indicators = results['indicators']
    price_changes = results['price_changes']
    
    # Display current data
    logger.info("\n" + "="*100)
    logger.info(f"CURRENT DATA - {symbol}")
    logger.info("="*100)
    logger.info(f"Current Price: ${current_data['lastPrice']:.6f}")
    logger.info(f"24h Volume: ${current_data['turnover24h']:.0f}")
    logger.info(f"24h % Change: {current_data['price24hPcnt']:.2f}%")
    logger.info(f"Mark Price: ${current_data['markPrice']:.6f}")
    logger.info(f"Index Price: ${current_data['indexPrice']:.6f}")
    
    # Display price changes
    logger.info("\n" + "="*100)
    logger.info("PRICE CHANGES (Multiple Timeframes)")
    logger.info("="*100)
    for timeframe, change in price_changes.items():
        if change is not None:
            direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            logger.info(f"{timeframe:12} {direction} {change:+.2f}%")
        else:
            logger.info(f"{timeframe:12} ⚠️  Not enough data")
    
    # Display technical indicators
    if indicators:
        logger.info("\n" + "="*100)
        logger.info("TECHNICAL INDICATORS")
        logger.info("="*100)
        
        logger.info(f"\nVolatility:")
        logger.info(f"  ATR(14): {indicators.get('atr_14', 'N/A'):.6f}")
        
        logger.info(f"\nTrend (Simple Moving Averages):")
        logger.info(f"  SMA(9):  ${indicators.get('sma_9', 'N/A'):.6f}")
        logger.info(f"  SMA(12): ${indicators.get('sma_12', 'N/A'):.6f}")
        logger.info(f"  SMA(26): ${indicators.get('sma_26', 'N/A'):.6f}")
        
        logger.info(f"\nSupport & Resistance (Bollinger Bands):")
        logger.info(f"  Upper Band: ${indicators.get('bb_high', 'N/A'):.6f}")
        logger.info(f"  Middle:     ${indicators.get('bb_ma', 'N/A'):.6f}")
        logger.info(f"  Lower Band: ${indicators.get('bb_low', 'N/A'):.6f}")
        
        logger.info(f"\nMomentum (Stochastic K):")
        stoch_k = indicators.get('stoch_k_14', 'N/A')
        if isinstance(stoch_k, (int, float)):
            if stoch_k < 20:
                status = "🔴 OVERSOLD (Potential Buy)"
            elif stoch_k > 80:
                status = "🟢 OVERBOUGHT (Potential Sell)"
            else:
                status = "🟡 NEUTRAL"
            logger.info(f"  Stoch_K(7,3): {stoch_k:.2f} {status}")
        else:
            logger.info(f"  Stoch_K(7,3): {stoch_k}")
    
    # Display analysis summary
    logger.info("\n" + "="*100)
    logger.info("ANALYSIS SUMMARY")
    logger.info("="*100)
    
    current_price = current_data['lastPrice']
    sma_9 = indicators.get('sma_9', None)
    sma_26 = indicators.get('sma_26', None)
    stoch_k = indicators.get('stoch_k_14', None)
    
    # Trend analysis
    if sma_9 and sma_26:
        if sma_9 > sma_26:
            logger.info("📈 Trend: UPTREND (SMA9 > SMA26)")
        else:
            logger.info("📉 Trend: DOWNTREND (SMA9 < SMA26)")
    
    # Price position
    if sma_9:
        if current_price > sma_9:
            logger.info(f"📍 Price Position: ABOVE SMA9 (${sma_9:.6f})")
        else:
            logger.info(f"📍 Price Position: BELOW SMA9 (${sma_9:.6f})")
    
    # Momentum
    if isinstance(stoch_k, (int, float)):
        if stoch_k < 20:
            logger.info("🔴 Momentum: OVERSOLD - Potential reversal upward")
        elif stoch_k > 80:
            logger.info("🟢 Momentum: OVERBOUGHT - Potential reversal downward")
        else:
            logger.info("🟡 Momentum: NEUTRAL - No extreme conditions")
    
    logger.info("\n" + "="*100)
    logger.info("Analysis Complete")
    logger.info("="*100)

if __name__ == '__main__':
    # Example usage
    symbol = "BTCUSDT"
    results = analyze_single_ticker(symbol, interval="1m", limit=200)
    display_single_ticker_analysis(results)
