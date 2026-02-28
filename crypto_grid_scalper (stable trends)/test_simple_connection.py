#!/usr/bin/env python3
"""
Simple test to verify Bybit API connection without external dependencies.
"""

import os
import sys
import json

def test_credentials():
    """Test if credentials are properly configured."""
    print("="*60)
    print("BYBIT API CONNECTION TEST")
    print("="*60)
    
    # Read .env file manually
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    credentials = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip().strip('"')
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    # Check required credentials
    api_key = credentials.get('BYBIT_API_KEY')
    api_secret = credentials.get('BYBIT_API_SECRET')
    testnet = credentials.get('TESTNET', 'True').lower() == 'true'
    symbol = credentials.get('SYMBOL', 'BTCUSDT')
    
    if not api_key or not api_secret:
        print("❌ API credentials not found in .env file")
        return False
    
    print("\n✓ Credentials loaded from .env")
    print(f"  - API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"  - API Secret: {api_secret[:10]}...{api_secret[-5:]}")
    print(f"  - Testnet: {testnet}")
    print(f"  - Symbol: {symbol}")
    
    # Try to import and test the exchange module
    print("\n" + "-"*60)
    print("Attempting to import Bybit SDK...")
    print("-"*60)
    
    try:
        from pybit.unified_trading import HTTP
        print("✓ Bybit SDK imported successfully")
        
        # Try to initialize the client
        print("\nInitializing Bybit API client...")
        client = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
        print("✓ Bybit API client initialized successfully")
        
        # Try to fetch market price
        print(f"\nFetching market price for {symbol}...")
        response = client.get_tickers(category="linear", symbol=symbol)
        
        if response['retCode'] == 0:
            data = response['result']['list'][0]
            mark_price = data['markPrice']
            print(f"✓ Market price for {symbol}: ${mark_price}")
        else:
            print(f"⚠ Could not fetch market price: {response['retMsg']}")
        
        print("\n" + "="*60)
        print("✓ CONNECTION TEST PASSED!")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Bybit SDK: {e}")
        print("\nTo fix this, install the required package:")
        print("  python3 -m pip install pybit")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_credentials()
    sys.exit(0 if success else 1)
