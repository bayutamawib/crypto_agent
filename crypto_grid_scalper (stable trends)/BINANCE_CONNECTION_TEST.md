# Binance API Connection Testing Guide

## Prerequisites

Before testing the connection, ensure you have the required dependencies installed:

```bash
python3 -m pip install -r requirements.txt
```

If you don't have pip installed, you may need to install it first:
- **Ubuntu/Debian**: `sudo apt-get install python3-pip`
- **Amazon Linux/RHEL**: `sudo yum install python3-pip`
- **macOS**: `brew install python3` (includes pip)

## Testing Methods

### Method 1: Run the Automated Test Script

Once dependencies are installed, run the test script:

```bash
python3 test_binance_connection.py
```

This will:
- ✓ Initialize the Binance API client
- ✓ Fetch the current market price for your configured symbol
- ✓ Retrieve symbol information (precision, filters)
- ✓ Get position information for the symbol

### Method 2: Manual Testing in Python REPL

```python
import os
from dotenv import load_dotenv
from src.exchange import Exchange

# Load environment variables
load_dotenv()

# Get credentials from .env
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
testnet = os.getenv('TESTNET', 'True').lower() == 'true'
symbol = os.getenv('SYMBOL', 'BTCUSDT')

# Initialize exchange
exchange = Exchange(api_key, api_secret, testnet=testnet)

# Test 1: Get market price
price = exchange.get_market_price(symbol)
print(f"Market price for {symbol}: ${price}")

# Test 2: Get symbol info
symbol_info = exchange.get_symbol_info(symbol)
print(f"Symbol info: {symbol_info}")

# Test 3: Get position info
position = exchange.get_position_information(symbol)
print(f"Position: {position}")
```

### Method 3: Test with curl (No Python Required)

Test the Binance API directly using curl:

```bash
# Get server time (no authentication required)
curl -s https://testnet.binancefuture.com/fapi/v1/time | jq .

# Get mark price (no authentication required)
curl -s "https://testnet.binancefuture.com/fapi/v1/premiumIndex?symbol=BTCUSDT" | jq .

# Get account information (requires authentication)
# Note: You'll need to generate a proper signature for authenticated requests
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'binance_sdk_derivatives_trading_usds_futures'"

**Solution**: Install the Binance SDK:
```bash
python3 -m pip install binance-sdk-derivatives-trading-usds-futures
```

### Issue: "API Error: Invalid API key"

**Possible causes**:
1. API key/secret in `.env` is incorrect
2. API key/secret has extra spaces or quotes
3. API key/secret has been revoked or regenerated

**Solution**: 
- Verify your credentials in the `.env` file
- Regenerate API keys from Binance dashboard if needed
- Ensure you're using testnet keys for `TESTNET=True`

### Issue: "Connection refused" or "Network error"

**Possible causes**:
1. Network connectivity issue
2. Binance API is temporarily down
3. Using wrong endpoint URL

**Solution**:
- Check your internet connection
- Verify the endpoint URL is correct:
  - Testnet: `https://testnet.binancefuture.com`
  - Mainnet: `https://fapi.binance.com`
- Check Binance status page: https://www.binance.com/en/support/announcement

### Issue: "Signature for this request is invalid"

**Cause**: API secret is incorrect or has been regenerated

**Solution**:
- Regenerate API keys from Binance dashboard
- Update `.env` file with new credentials
- Ensure no extra spaces or characters in the secret

## Configuration

The connection uses settings from `.env`:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
TESTNET=True  # Set to False for mainnet
SYMBOL=BTCUSDT
```

## Security Notes

⚠️ **Important**: 
- Never commit `.env` file to version control
- Use testnet keys for development/testing
- Rotate API keys regularly
- Use IP whitelisting in Binance API settings
- Restrict API key permissions to only what's needed

## Next Steps

Once the connection is verified:
1. Test the grid trading bot with small position sizes
2. Monitor logs in `bot.log`
3. Review the `QUICKSTART.md` for running the bot
