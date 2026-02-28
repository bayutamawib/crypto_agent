#!/usr/bin/env python3
"""
Test script to verify Bybit API connection and credentials.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_connection():
    """Test Bybit API connection."""
    try:
        from exchange import Exchange
        
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        testnet = os.getenv('TESTNET', 'True').lower() == 'true'
        
        if not api_key or not api_secret:
            logger.error("❌ API credentials not found in .env file")
            return False
        
        logger.info(f"Testing connection to Bybit {'Testnet' if testnet else 'Mainnet'}...")
        logger.info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
        
        # Initialize exchange client
        exchange = Exchange(api_key, api_secret, testnet=testnet)
        logger.info("✓ Exchange client initialized successfully")
        
        # Test 1: Get market price
        symbol = os.getenv('SYMBOL', 'BTCUSDT')
        logger.info(f"\nTest 1: Fetching market price for {symbol}...")
        price = exchange.get_market_price(symbol)
        if price:
            logger.info(f"✓ Market price for {symbol}: ${price}")
        else:
            logger.warning(f"⚠ Could not fetch market price")
            return False
        
        # Test 2: Get symbol info
        logger.info(f"\nTest 2: Fetching symbol info for {symbol}...")
        symbol_info = exchange.get_symbol_info(symbol)
        if symbol_info:
            logger.info(f"✓ Symbol info retrieved")
            # Extract filter information from Bybit response
            qty_step = None
            tick_size = None
            lot_size_filter = symbol_info.get('lotSizeFilter', {})
            price_filter = symbol_info.get('priceFilter', {})
            qty_step = lot_size_filter.get('qtyStep')
            tick_size = price_filter.get('tickSize')
            logger.info(f"  - Quantity step: {qty_step}")
            logger.info(f"  - Price step: {tick_size}")
        else:
            logger.warning(f"⚠ Could not fetch symbol info")
            return False
        
        # Test 3: Get position information
        logger.info(f"\nTest 3: Fetching position information for {symbol}...")
        position = exchange.get_position_information(symbol)
        if position:
            logger.info(f"✓ Position info retrieved")
            logger.info(f"  - Position amount: {position['positionAmt']}")
            logger.info(f"  - Entry price: {position['entryPrice']}")
        else:
            logger.warning(f"⚠ Could not fetch position info (may be normal if no position)")
        
        logger.info("\n" + "="*50)
        logger.info("✓ All connection tests passed!")
        logger.info("="*50)
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
