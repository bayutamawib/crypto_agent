from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from .config import BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_TESTNET
import pandas as pd
from .logger import get_logger

logger = get_logger(__name__)

def get_binance_client():
    """
    Initializes and returns a Binance API client.

    For this to work, you must have a Binance account with API credentials.
    You must also have the BINANCE_API_KEY and BINANCE_API_SECRET environment 
    variables set in your .env file.

    Args:
        testnet (bool): If True, uses testnet. If False, uses mainnet.

    Returns:
        Client: An authenticated Binance API client.
    """
    try:
        if BINANCE_TESTNET:
            # Testnet endpoints
            client = Client(
                api_key=BINANCE_API_KEY,
                api_secret=BINANCE_API_SECRET,
                testnet=True
            )
        else:
            # Mainnet
            client = Client(
                api_key=BINANCE_API_KEY,
                api_secret=BINANCE_API_SECRET
            )
        logger.info(f"Binance client initialized (testnet={BINANCE_TESTNET})")
        return client
    except Exception as e:
        logger.error(f"Error initializing Binance client: {e}")
        logger.error("Please ensure you have valid Binance API credentials in your .env file.")
        return None

def get_market_data_from_binance(binance_client: Client, limit: int = 50):
    """
    Fetches market data from the Binance API.

    Args:
        binance_client (Client): An authenticated Binance API client.
        limit (int): The number of tickers to fetch.

    Returns:
        pd.DataFrame: A DataFrame containing the market data with columns:
                      symbol, lastPrice, price24hPcnt, turnover24h
    """
    try:
        logger.info(f"Fetching market data from Binance...")
        
        # Fetch 24hr ticker data
        response = binance_client.get_ticker()
        
        if not response:
            logger.error("Binance API returned empty response")
            return pd.DataFrame()
        
        # Convert to DataFrame and filter
        data = []
        for ticker in response[:limit]:
            # Only include USDT pairs
            if ticker['symbol'].endswith('USDT'):
                data.append({
                    'symbol': ticker['symbol'],
                    'lastPrice': float(ticker['lastPrice']),
                    'price24hPcnt': float(ticker['priceChangePercent']),  # Already in percentage
                    'turnover24h': float(ticker['quoteAssetVolume']),  # Volume in USDT
                    'volume24h': float(ticker['volume']),
                    'markPrice': float(ticker['lastPrice']),  # Binance doesn't have separate mark price for spot
                    'indexPrice': float(ticker['lastPrice']),  # Binance doesn't have index price for spot
                })
        
        df = pd.DataFrame(data)
        logger.info(f"Fetched {len(df)} USDT tickers from Binance")
        return df
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}")
        return pd.DataFrame()
    except BinanceRequestException as e:
        logger.error(f"Binance request error: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching market data from Binance: {e}")
        return pd.DataFrame()

def get_klines_from_binance(binance_client: Client, symbol: str, interval: str = "1m", limit: int = 100):
    """
    Fetches candlestick (OHLCV) data from Binance API.

    Args:
        binance_client (Client): An authenticated Binance API client.
        symbol (str): The trading pair symbol (e.g., BTCUSDT).
        interval (str): The candlestick interval (1m, 5m, 15m, 1h, 4h, 1d, etc.).
        limit (int): The number of candlesticks to fetch (max 1000).

    Returns:
        pd.DataFrame: A DataFrame with OHLCV data.
    """
    try:
        logger.info(f"Fetching klines for {symbol} (interval={interval})...")
        
        # Convert interval format if needed (from Bybit format to Binance format)
        interval_map = {
            "1": "1m",
            "3": "3m",
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "120": "2h",
            "240": "4h",
            "360": "6h",
            "720": "12h",
            "D": "1d",
            "W": "1w",
            "M": "1M",
        }
        
        binance_interval = interval_map.get(interval, interval)
        
        klines = binance_client.get_klines(
            symbol=symbol,
            interval=binance_interval,
            limit=limit
        )
        
        if not klines:
            logger.error(f"No klines data for {symbol}")
            return pd.DataFrame()
        
        data = []
        for kline in klines:
            data.append({
                'timestamp': int(kline[0]),
                'Open': float(kline[1]),
                'High': float(kline[2]),
                'Low': float(kline[3]),
                'Close': float(kline[4]),
                'Volume': float(kline[7]),  # Quote asset volume (USDT)
            })
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        logger.info(f"Fetched {len(df)} klines for {symbol}")
        return df
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error fetching klines for {symbol}: {e}")
        return pd.DataFrame()
    except BinanceRequestException as e:
        logger.error(f"Binance request error fetching klines for {symbol}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching klines for {symbol}: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    binance_client = get_binance_client()
    if binance_client:
        market_data = get_market_data_from_binance(binance_client)
        print(market_data)
        
        if not market_data.empty:
            symbol = market_data.iloc[0]['symbol']
            klines = get_klines_from_binance(binance_client, symbol)
            print(klines)
