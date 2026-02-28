# Binance Grid Scalper - Complete Index

## 📋 Documentation Files

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Start here! Step-by-step setup guide
- **[README.md](README.md)** - Full feature documentation and usage guide

### Technical Documentation
- **[MIGRATION_NOTES.md](MIGRATION_NOTES.md)** - Detailed API changes from Bybit to Binance
- **[COMPARISON.md](COMPARISON.md)** - Side-by-side comparison of Bybit vs Binance versions
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was created and how

### Configuration
- **[.env.example.txt](.env.example.txt)** - Example configuration file
- **[.env](.env)** - Your configuration file (edit with your API keys)

## 🐍 Python Source Files

### Core Modules (`src/`)

| File | Purpose |
|------|---------|
| `bot.py` | Main trading bot logic and order placement |
| `exchange.py` | Binance API wrapper with all trading operations |
| `config.py` | Configuration loader from environment variables |
| `grid.py` | Grid level generation algorithm |
| `risk.py` | Risk management and exit condition checking |
| `logger.py` | Logging configuration |
| `utils.py` | Shared utility functions |
| `__init__.py` | Package initialization |

### Entry Point
| File | Purpose |
|------|---------|
| `main.py` | Application entry point - run this to start the bot |

## 📦 Dependencies

- **binance-sdk-derivatives-trading-usds-futures** - Official Binance SDK
- **python-dotenv** - Environment variable management

See `requirements.txt` for exact versions.

## 🚀 Quick Start

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Edit `.env` with your Binance API keys
3. **Run**: `python main.py`
4. **Monitor**: Check `bot.log` for operation logs

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## 📊 Key Features

### Trading
- ✅ Grid trading with configurable levels
- ✅ Long and short mode support
- ✅ Configurable leverage (1-125x)
- ✅ Position sizing (BASE or QUOTE)

### Risk Management
- ✅ Stop loss percentage-based exits
- ✅ Take profit percentage-based exits
- ✅ 75% range exit rule
- ✅ 3-position consecutive rule

### Operations
- ✅ Testnet support
- ✅ Comprehensive logging
- ✅ Graceful shutdown
- ✅ Error handling and recovery

## 🔧 Configuration Parameters

Edit `.env` to customize:

```env
# API Credentials
BINANCE_API_KEY="your_key"
BINANCE_API_SECRET="your_secret"

# Trading Strategy
MODE="long"                    # long or short
SYMBOL="BTCUSDT"              # Trading pair
LEVERAGE=20                   # Leverage multiplier
START_PRICE=60000             # Grid lower bound
END_PRICE=70000               # Grid upper bound
GRID_SIZE=100                 # Number of grid levels

# Position Sizing
POSITION_SIZE_TYPE="QUOTE"    # QUOTE or BASE
POSITION_SIZE=10.0            # Size per order

# Risk Management
ENABLE_RANGE_EXIT_RULE="True" # Enable 75% range exit
TAKE_PROFIT_PERCENT=5         # Take profit %
STOP_LOSS_PERCENT=2           # Stop loss %

# Environment
TESTNET="True"                # Use testnet
```

## 📝 How It Works

### Grid Generation
1. Bot gets current market price
2. Generates grid levels centered at current price
3. Places limit orders at each level
4. For LONG: BUY orders below price
5. For SHORT: SELL orders above price

### Position Management
1. Monitors filled orders (open positions)
2. Tracks consecutive position count
3. Checks exit conditions:
   - Stop loss hit
   - Take profit hit
   - 75% range exceeded
   - 3 consecutive positions

### Exit Process
1. Cancels all pending orders
2. Closes open position with market order
3. Resets position counter
4. Generates new grid

## 🧪 Testing

### Testnet Setup
1. Create account: https://testnet.binancefuture.com
2. Generate API keys
3. Set `TESTNET="True"` in `.env`
4. Run with small position sizes

### Verification
- Check `bot.log` for operation logs
- Monitor grid order placement
- Verify position tracking
- Test exit conditions

## 📊 Monitoring

### Log File
```bash
tail -f bot.log          # Watch logs in real-time
cat bot.log              # View full log
```

### Log Levels
- **INFO**: Normal operations
- **WARNING**: Exit triggers, important events
- **ERROR**: API errors, exceptions
- **DEBUG**: Detailed operation info

## 🛑 Stopping the Bot

Create `.close_now` file to gracefully shutdown:
```bash
touch .close_now
```

The bot will:
1. Cancel all pending orders
2. Close any open positions
3. Exit cleanly

## ⚠️ Risk Management

**Important**: Grid trading involves significant risk!

- Always use stop loss and take profit
- Start with small position sizes
- Test thoroughly on testnet first
- Never trade with funds you can't afford to lose
- Monitor bot operation closely
- Use appropriate leverage

## 🔗 Resources

### Binance Documentation
- [Binance Futures API](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)
- [Binance Testnet](https://testnet.binancefuture.com)
- [Official SDK](https://github.com/binance/binance-connector-python)

### Related Documentation
- [MIGRATION_NOTES.md](MIGRATION_NOTES.md) - API migration details
- [COMPARISON.md](COMPARISON.md) - Bybit vs Binance comparison
- [README.md](README.md) - Full documentation

## 📂 File Structure

```
crypto_grid_scalper_binance/
├── src/                          # Source code
│   ├── bot.py                   # Main bot logic
│   ├── exchange.py              # Binance API wrapper
│   ├── config.py                # Configuration
│   ├── grid.py                  # Grid generation
│   ├── risk.py                  # Risk management
│   ├── logger.py                # Logging
│   ├── utils.py                 # Utilities
│   └── __init__.py              # Package init
├── main.py                       # Entry point
├── requirements.txt              # Dependencies
├── .env                          # Configuration (your keys)
├── .env.example.txt              # Configuration example
├── .gitignore                    # Git ignore rules
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Quick start guide
├── MIGRATION_NOTES.md            # API migration guide
├── COMPARISON.md                 # Bybit vs Binance
├── IMPLEMENTATION_SUMMARY.md     # Implementation details
├── INDEX.md                      # This file
└── bot.log                       # Log file (created at runtime)
```

## 🎯 Next Steps

1. **Read**: Start with [QUICKSTART.md](QUICKSTART.md)
2. **Setup**: Install dependencies and configure `.env`
3. **Test**: Run on testnet with small position sizes
4. **Monitor**: Watch logs and positions closely
5. **Optimize**: Adjust parameters based on results
6. **Deploy**: Move to mainnet when confident

## 💡 Tips

- Start with `TESTNET="True"` and small `POSITION_SIZE`
- Monitor `bot.log` for any issues
- Use `ENABLE_RANGE_EXIT_RULE="True"` for safety
- Set reasonable `TAKE_PROFIT_PERCENT` and `STOP_LOSS_PERCENT`
- Test different `GRID_SIZE` values for your strategy
- Keep `LEVERAGE` conservative initially

## ❓ Troubleshooting

See [README.md](README.md) for common issues and solutions.

## 📞 Support

For issues:
1. Check `bot.log` for error messages
2. Review [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for API details
3. Check [Binance API Documentation](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Status**: Production Ready
