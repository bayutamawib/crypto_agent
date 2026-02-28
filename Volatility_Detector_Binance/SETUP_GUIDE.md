# Volatility Detector Binance - Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd Volatility_Detector_Binance
pip install -r requirements.txt
```

### 2. Configure API Credentials

Edit `.env` file with your Binance API credentials:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=false
```

**To get Binance API credentials:**
1. Go to https://www.binance.com/en/account/api-management
2. Create a new API key
3. Enable "Read" permissions (minimum required)
4. Copy API Key and Secret to `.env`

### 3. Test the Installation

```bash
# Test with a simple analysis
python -m src.bot.analyze_ticker BTCUSDT --json
```

Expected output:
```json
{
  "symbol": "BTCUSDT",
  "trend": "UPTREND",
  "momentum": "OVERBOUGHT",
  "stoch_k": 87.23,
  "sma_9": 64877.33,
  "sma_26": 64721.65,
  "current_price": 64962.10
}
```

## Configuration Options

### Technical Indicators (.env)

```
# Stochastic K Configuration
STOCH_K_PERIOD=7              # Period for Stochastic calculation (default: 7)
STOCH_K_SMOOTHING=3           # Smoothing period (default: 3)

# Single Ticker Analysis
SINGLE_TICKER_INTERVAL=1m     # Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
SINGLE_TICKER_LIMIT=200       # Number of candles to fetch (max: 1000)
```

### Binance Interval Formats

Supported intervals for `SINGLE_TICKER_INTERVAL`:
- `1m`, `3m`, `5m`, `15m`, `30m` - Minutes
- `1h`, `2h`, `4h`, `6h`, `12h` - Hours
- `1d`, `3d` - Days
- `1w` - Weeks
- `1M` - Months

## Usage Examples

### 1. Basic Analysis (Human-Readable)

```bash
python -m src.bot.analyze_ticker BTCUSDT
```

Output includes:
- Current price and 24h stats
- Price changes over multiple timeframes
- Technical indicators (SMA, Stochastic K, ATR, Bollinger Bands)
- Trend and momentum analysis

### 2. JSON Output (For Bot Integration)

```bash
python -m src.bot.analyze_ticker BTCUSDT --json
```

Perfect for piping to other tools or parsing in scripts.

### 3. Custom Interval and Limit

```bash
# Analyze with 5-minute candles, 100 candles
python -m src.bot.analyze_ticker ETHUSDT 5m 100

# Analyze with 1-hour candles, 200 candles
python -m src.bot.analyze_ticker BNBUSDT 1h 200
```

### 4. Integration with Grid Bot

The Binance Volatility Detector can be integrated with the grid scalper bot by:

1. Updating the grid bot's `VOLATILITY_DETECTOR_PATH` to point to this folder
2. Changing the command to use Binance API format
3. Updating the interval format in the command

Example in grid bot's `market_position_manager.py`:
```python
cmd = [
    'python', '-m', 'src.bot.analyze_ticker',
    symbol,
    self.config['singleTickerInterval'],  # e.g., "1m"
    str(self.config['singleTickerLimit']),
    '--json'
]
```

## Troubleshooting

### Issue: "API key invalid"
- Verify API credentials in `.env`
- Check that API key has "Read" permissions enabled
- Ensure no extra spaces in `.env` values

### Issue: "Symbol not found"
- Verify symbol exists on Binance (e.g., BTCUSDT, ETHUSDT)
- Check symbol is in uppercase
- Ensure symbol is a USDT trading pair

### Issue: "Not enough data"
- Increase `SINGLE_TICKER_LIMIT` in `.env`
- Minimum required: 26 candles (for SMA(26))
- Recommended: 200+ candles for accurate analysis

### Issue: "Connection timeout"
- Check internet connection
- Verify Binance API is accessible
- Try with testnet first: `BINANCE_TESTNET=true`

## File Structure

```
Volatility_Detector_Binance/
├── .env                          # Configuration (API keys, settings)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # Main documentation
├── SETUP_GUIDE.md               # This file
└── src/
    ├── __init__.py
    └── bot/
        ├── __init__.py
        ├── config.py             # Configuration loader
        ├── binance_api.py        # Binance API wrapper
        ├── logger.py             # Logging setup
        ├── indicators.py         # Technical indicators
        ├── single_ticker_analysis.py  # Analysis module
        └── analyze_ticker.py     # CLI entry point
```

## Key Differences from Bybit Version

| Feature | Bybit | Binance |
|---------|-------|---------|
| API Library | pybit | python-binance |
| Interval Format | "1", "5", "60" | "1m", "5m", "1h" |
| Market Type | Futures (linear/inverse) | Spot |
| Mark Price | Available | N/A (uses last price) |
| Index Price | Available | N/A (uses last price) |

## Next Steps

1. **Test with different symbols**: Try ETHUSDT, BNBUSDT, etc.
2. **Experiment with intervals**: Test 5m, 15m, 1h candles
3. **Monitor logs**: Check `LOG_LEVEL` in `.env` for debugging
4. **Integrate with bot**: Use JSON output in your trading bot

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the SETUP_GUIDE.md (this file)
3. Check logs for error messages
4. Verify API credentials and permissions
