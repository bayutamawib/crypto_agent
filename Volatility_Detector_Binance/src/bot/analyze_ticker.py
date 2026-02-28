"""
Command-line interface for single ticker analysis
Usage: python -m src.bot.analyze_ticker BTCUSDT
"""

import sys
import json
import logging
import pandas as pd
from .single_ticker_analysis import analyze_single_ticker, display_single_ticker_analysis
from .logger import get_logger
from .config import SINGLE_TICKER_INTERVAL, SINGLE_TICKER_LIMIT

logger = get_logger(__name__)

def extract_trend_and_momentum(results: dict):
    """
    Extracts trend and momentum from analysis results.
    
    Args:
        results (dict): Analysis results from analyze_single_ticker()
    
    Returns:
        dict: Structured data with trend and momentum
    """
    if results is None:
        logger.error("Analysis results are None - analysis failed")
        return None
    
    indicators = results.get('indicators', {})
    current_data = results.get('current_data', {})
    
    # Determine Trend
    sma_9 = indicators.get('sma_9', None)
    sma_26 = indicators.get('sma_26', None)
    
    trend = None
    if sma_9 and sma_26:
        trend = "UPTREND" if sma_9 > sma_26 else "DOWNTREND"
    
    # Determine Momentum
    stoch_k = indicators.get('stoch_k_14', None)
    momentum = None
    
    if isinstance(stoch_k, (int, float)):
        if stoch_k < 20:
            momentum = "OVERSOLD"
        elif stoch_k > 80:
            momentum = "OVERBOUGHT"
        else:
            momentum = "NEUTRAL"
    
    result = {
        'symbol': results.get('symbol'),
        'trend': trend,
        'momentum': momentum,
        'stoch_k': stoch_k,
        'sma_9': sma_9,
        'sma_26': sma_26,
        'current_price': current_data.get('lastPrice'),
    }
    
    logger.info(f"Extracted trend and momentum: {result}")
    return result

def main():
    """Main entry point for single ticker analysis"""
    
    # Get ticker from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m src.bot.analyze_ticker <TICKER> [--json]")
        print("\nExamples:")
        print("  python -m src.bot.analyze_ticker BTCUSDT")
        print("  python -m src.bot.analyze_ticker BTCUSDT --json")
        print("  python -m src.bot.analyze_ticker ETHUSDT 5m 100")
        print("    (interval=5m, limit=100 candles)")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    output_json = "--json" in sys.argv
    
    # Parse optional parameters
    interval = SINGLE_TICKER_INTERVAL
    limit = SINGLE_TICKER_LIMIT
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--json":
            continue
        elif i == 2:
            interval = arg
        elif i == 3:
            limit = int(arg)
    
    # Suppress all logging when outputting JSON
    if output_json:
        # Disable all loggers
        logging.getLogger().setLevel(logging.CRITICAL)
        for logger_name in logging.Logger.manager.loggerDict:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    
    # Perform analysis
    results = analyze_single_ticker(symbol, interval=interval, limit=limit)
    
    if output_json:
        # Output as JSON for programmatic parsing (no display_single_ticker_analysis call)
        if results is None:
            # If analysis failed, output error JSON
            error_output = {
                'symbol': symbol,
                'trend': None,
                'momentum': None,
                'stoch_k': None,
                'sma_9': None,
                'sma_26': None,
                'current_price': None,
                'error': 'Analysis failed - could not fetch data'
            }
            print(json.dumps(error_output, indent=2))
        else:
            trend_momentum = extract_trend_and_momentum(results)
            if trend_momentum is None:
                # If extraction failed, output error JSON
                error_output = {
                    'symbol': symbol,
                    'trend': None,
                    'momentum': None,
                    'stoch_k': None,
                    'sma_9': None,
                    'sma_26': None,
                    'current_price': None,
                    'error': 'Failed to extract trend and momentum'
                }
                print(json.dumps(error_output, indent=2))
            else:
                print(json.dumps(trend_momentum, indent=2))
    else:
        # Display results in human-readable format
        display_single_ticker_analysis(results)

if __name__ == "__main__":
    main()
