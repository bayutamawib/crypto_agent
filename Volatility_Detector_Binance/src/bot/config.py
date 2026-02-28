import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Binance API Credentials
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "false").lower() == "true"

# Database
DB_PATH = os.getenv("DB_PATH", "data/bot_trader.db")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Trading Parameters
MIN_VOLUME_USDT = float(os.getenv("MIN_VOLUME_USDT", "1000000"))
PRICE_CHANGE_MIN = float(os.getenv("PRICE_CHANGE_MIN", "15"))
PRICE_CHANGE_MAX = float(os.getenv("PRICE_CHANGE_MAX", "40"))

# Timeframes (in minutes)
TIMEFRAME_1 = 60  # 1 hour
TIMEFRAME_2 = 120  # 2 hours

# Technical Indicators
STOCH_K_PERIOD = int(os.getenv("STOCH_K_PERIOD", "7"))
STOCH_K_SMOOTHING = int(os.getenv("STOCH_K_SMOOTHING", "3"))
SMA_PERIODS = [9, 12, 26]
ATR_PERIOD = 14
BB_PERIOD = 20

# Single Ticker Analysis Configuration
SINGLE_TICKER_INTERVAL = os.getenv("SINGLE_TICKER_INTERVAL", "1m")
SINGLE_TICKER_LIMIT = int(os.getenv("SINGLE_TICKER_LIMIT", "200"))
