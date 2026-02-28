# Volatility Detector Binance - Quick Start

## 30-Second Setup

### 1. Install
```bash
cd Volatility_Detector_Binance
pip install -r requirements.txt
```

### 2. Configure
Edit `.env`:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

### 3. Test
```bash
python -m src.bot.analyze_ticker BTCUSDT --json
```

## Common Commands

### Analyze Bitcoin
```bash
python -m src.bot.analyze_ticker BTCUSDT --json
```

### Analyze Ethereum
```bash
python -m src.bot.analyze_ticker ETHUSDT --json
```

### Analyze with 5-minute candles
```bash
python -m src.bot.analyze_ticker BTCUSDT 5m 200 --json
```

### Human-readable output
```bash
python -m src.bot.analyze_ticker BTCUSDT
```

## Output Explanation

```json
{
  "symbol": "BTCUSDT",           # Trading pair
  "trend": "UPTREND",            # UPTREND or DOWNTREND
  "momentum": "OVERBOUGHT",      # OVERBOUGHT, OVERSOLD, or NEUTRAL
  "stoch_k": 87.23,              # Stochastic K value (0-100)
  "sma_9": 64877.33,             # 9-period moving average
  "sma_26": 64721.65,            # 26-period moving average
  "current_price": 64962.10      # Current market price
}
```

## Trading Signals

| Trend | Momentum | Signal |
|-------|----------|--------|
| UPTREND | OVERBOUGHT | 🟢 Strong Buy |
| DOWNTREND | OVERSOLD | 🔴 Strong Sell |
| Any | NEUTRAL | 🟡 Neutral |

## Troubleshooting

**"API key invalid"**
- Check `.env` file
- Verify API key and secret are correct
- Ensure no extra spaces

**"Symbol not found"**
- Use uppercase (BTCUSDT, not btcusdt)
- Ensure it's a USDT pair
- Check symbol exists on Binance

**"Not enough data"**
- Increase limit: `python -m src.bot.analyze_ticker BTCUSDT 1m 500`
- Need at least 26 candles

## Next Steps

1. Read `README.md` for detailed documentation
2. Read `SETUP_GUIDE.md` for advanced configuration
3. Check `BINANCE_VS_BYBIT_COMPARISON.md` to compare with Bybit version
4. Integrate with your trading bot using JSON output

## File Structure

```
Volatility_Detector_Binance/
├── .env                    # Your API credentials
├── requirements.txt        # Dependencies
├── README.md              # Full documentation
├── SETUP_GUIDE.md         # Detailed setup
├── QUICK_START.md         # This file
└── src/bot/
    ├── binance_api.py     # Binance API wrapper
    ├── indicators.py      # Technical indicators
    ├── analyze_ticker.py  # CLI tool
    └── config.py          # Configuration
```

## Support

- **Documentation**: See README.md
- **Setup Help**: See SETUP_GUIDE.md
- **Comparison**: See BINANCE_VS_BYBIT_COMPARISON.md
- **Errors**: Check logs with `LOG_LEVEL=DEBUG` in .env
