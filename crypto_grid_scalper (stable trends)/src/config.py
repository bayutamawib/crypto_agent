# src/config.py

import os
from dotenv import load_dotenv

def load_config():
    """
    Loads configuration from environment variables.
    This is where you would validate the config parameters.
    """
    load_dotenv() # take environment variables from .env.

    config = {
        "mode": os.getenv("MODE", "long"),
        "symbol": os.getenv("SYMBOL", "BTCUSDT"),
        "leverage": int(os.getenv("LEVERAGE", 20)),
        "startPrice": float(os.getenv("START_PRICE", 60000)),
        "endPrice": float(os.getenv("END_PRICE", 70000)),
        "gridSize": float(os.getenv("GRID_SIZE", 100)),
        "positionSizeType": os.getenv("POSITION_SIZE_TYPE", "QUOTE"),
        "positionSize": float(os.getenv("POSITION_SIZE", 10)),
        "enableRangeExitRule": os.getenv("ENABLE_RANGE_EXIT_RULE", "True").lower() == "true",
        "rangeExitThresholdPercent": float(os.getenv("RANGE_EXIT_THRESHOLD_PERCENT", 100)),
        "tpMode": os.getenv("TP_MODE", "PERCENTAGE"),
        "takeProfitPercent": float(os.getenv("TAKE_PROFIT_PERCENT", 0)) or None,
        "stopLossPercent": float(os.getenv("STOP_LOSS_PERCENT", 0)) or None,
        "bybitApiKey": os.getenv("BYBIT_API_KEY"),
        "bybitApiSecret": os.getenv("BYBIT_API_SECRET"),
        "testnet": os.getenv("TESTNET", "True").lower() == "true",
        "dualSidePosition": os.getenv("DUAL_SIDE_POSITION", "False").lower() == "true",
        # Market Position Logic Configuration
        "enableMarketPositionLogic": os.getenv("ENABLE_MARKET_POSITION_LOGIC", "True").lower() == "true",
        "analysisIntervalMinutes": int(os.getenv("ANALYSIS_INTERVAL_MINUTES", 10)),
        "volatilityDetectorMaxRetries": int(os.getenv("VOLATILITY_DETECTOR_MAX_RETRIES", 3)),
        "volatilityDetectorPath": os.getenv("VOLATILITY_DETECTOR_PATH", "../Volatility_Detector_Crypto"),
        # Grid Position Reopening Logic
        "enablePositionReopen": os.getenv("ENABLE_POSITION_REOPEN", "True").lower() == "true",
        "maxConsecutiveGridPositions": os.getenv("MAX_CONSECUTIVE_GRID_POSITIONS", "3"),
        "gridBotNeutralOnly": os.getenv("GRID_BOT_NEUTRAL_ONLY", "False").lower() == "true",
        # Market Position Reopening Logic
        "maxMarketPositionReopens": os.getenv("MAX_MARKET_POSITION_REOPENS", "unlimited"),
        # Neutral Momentum Behavior
        "neutralMomentumAction": os.getenv("NEUTRAL_MOMENTUM_ACTION", "stop"),  # "stop" or "continue"
        # Single Ticker Analysis Configuration
        "singleTickerInterval": os.getenv("SINGLE_TICKER_INTERVAL", "1"),
        "singleTickerLimit": int(os.getenv("SINGLE_TICKER_LIMIT", "200")),
    }

    # Basic validation
    if not all([config["bybitApiKey"], config["bybitApiSecret"]]):
        raise ValueError("Bybit API key and secret must be provided.")

    if config["mode"] not in ["long", "short", "neutral"]:
        raise ValueError("Mode must be either 'long', 'short', or 'neutral'.")

    if config["tpMode"] not in ["PERCENTAGE", "GRID_RANGE"]:
        raise ValueError("TP_MODE must be either 'PERCENTAGE' or 'GRID_RANGE'.")

    return config
