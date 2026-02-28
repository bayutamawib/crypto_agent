# Volatility Detector Binance - Documentation Index

## Getting Started

1. **[QUICK_START.md](QUICK_START.md)** - Start here! 30-second setup guide
2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup and configuration
3. **[README.md](README.md)** - Full documentation

## Reference

- **[BINANCE_VS_BYBIT_COMPARISON.md](../BINANCE_VS_BYBIT_COMPARISON.md)** - Compare with Bybit version
- **[requirements.txt](requirements.txt)** - Python dependencies

## File Structure

```
Volatility_Detector_Binance/
├── Documentation
│   ├── INDEX.md                 # This file
│   ├── QUICK_START.md          # 30-second setup
│   ├── SETUP_GUIDE.md          # Detailed setup
│   ├── README.md               # Full documentation
│   └── ../BINANCE_VS_BYBIT_COMPARISON.md
│
├── Configuration
│   ├── .env                    # API credentials (edit this!)
│   ├── .gitignore              # Git ignore rules
│   └── requirements.txt        # Python dependencies
│
└── Source Code
    └── src/bot/
        ├── binance_api.py      # Binance API wrapper
        ├── config.py           # Configuration loader
        ├── logger.py           # Logging setup
        ├── indicators.py       # Technical indicators
        ├── single_ticker_analysis.py  # Analysis module
        └── analyze_ticker.py   # CLI entry point
```

## Quick Navigation

### I want to...

**Get started quickly**
→ Read [QUICK_START.md](QUICK_START.md)

**Set up properly**
→ Read [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Understand all features**
→ Read [README.md](README.md)

**Compare with Bybit**
→ Read [BINANCE_VS_BYBIT_COMPARISON.md](../BINANCE_VS_BYBIT_COMPARISON.md)

**Install dependencies**
→ Run `pip install -r requirements.txt`

**Configure API credentials**
→ Edit `.env` file

**Test the installation**
→ Run `python -m src.bot.analyze_ticker BTCUSDT --json`

**Analyze a cryptocurrency**
→ Run `python -m src.bot.analyze_ticker SYMBOL --json`

**Integrate with my bot**
→ Use JSON output from analyze_ticker command

## Key Concepts

### Technical Indicators

- **SMA (9, 12, 26)** - Trend identification
- **Stochastic K (7, 3)** - Momentum analysis
- **ATR (14)** - Volatility measurement
- **Bollinger Bands (20)** - Support/resistance

### Trend Signals

- **UPTREND** - SMA(9) > SMA(26)
- **DOWNTREND** - SMA(9) < SMA(26)

### Momentum Signals

- **OVERBOUGHT** - Stochastic K > 80
- **OVERSOLD** - Stochastic K < 20
- **NEUTRAL** - Stochastic K between 20-80

### Trading Signals

| Trend | Momentum | Signal |
|-------|----------|--------|
| UPTREND | OVERBOUGHT | 🟢 Strong Buy |
| DOWNTREND | OVERSOLD | 🔴 Strong Sell |
| Any | NEUTRAL | 🟡 Neutral |

## Common Commands

```bash
# Analyze Bitcoin
python -m src.bot.analyze_ticker BTCUSDT --json

# Analyze Ethereum
python -m src.bot.analyze_ticker ETHUSDT --json

# Analyze with 5-minute candles
python -m src.bot.analyze_ticker BTCUSDT 5m 200 --json

# Human-readable output
python -m src.bot.analyze_ticker BTCUSDT

# Test installation
python -m src.bot.analyze_ticker BTCUSDT --json
```

## Troubleshooting

**Problem: "API key invalid"**
- Solution: Check `.env` file, verify credentials

**Problem: "Symbol not found"**
- Solution: Use uppercase (BTCUSDT), ensure USDT pair

**Problem: "Not enough data"**
- Solution: Increase limit (e.g., 500 candles)

**Problem: "Connection timeout"**
- Solution: Check internet, verify Binance API is accessible

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting.

## API Credentials

Get your Binance API credentials:
1. Go to https://www.binance.com/en/account/api-management
2. Create new API key
3. Enable "Read" permissions
4. Copy to `.env` file

## Next Steps

1. ✅ Read [QUICK_START.md](QUICK_START.md)
2. ✅ Edit `.env` with your API credentials
3. ✅ Run `pip install -r requirements.txt`
4. ✅ Test with `python -m src.bot.analyze_ticker BTCUSDT --json`
5. ✅ Integrate with your trading bot

## Support

- **Setup Issues**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Feature Questions**: See [README.md](README.md)
- **Comparison**: See [BINANCE_VS_BYBIT_COMPARISON.md](../BINANCE_VS_BYBIT_COMPARISON.md)
- **Errors**: Check logs with `LOG_LEVEL=DEBUG` in `.env`

## Version Information

- **Version**: 1.0.0
- **API**: Binance
- **Market**: Spot
- **Python**: 3.8+
- **Status**: Production Ready

---

**Ready to get started?** → [QUICK_START.md](QUICK_START.md)
