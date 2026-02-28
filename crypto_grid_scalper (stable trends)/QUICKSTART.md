# Quick Start Guide - Binance Grid Scalper

## 1. Setup

### Install Dependencies
```bash
cd crypto_grid_scalper_binance
pip install -r requirements.txt
```

### Configure API Keys
Edit `.env` file with your Binance API credentials:
```env
BINANCE_API_KEY="your_key_here"
BINANCE_API_SECRET="your_secret_here"
TESTNET="True"  # Start with testnet
```

## 2. Get Binance Testnet Credentials

1. Go to https://testnet.binancefuture.com
2. Create an account
3. Generate API Key:
   - Click on your profile → API Management
   - Create New Key
   - Enable Futures Trading
   - Copy API Key and Secret to `.env`

## 3. Configure Trading Parameters

Edit `.env` to set your trading strategy:

```env
# Trading pair
SYMBOL="BTCUSDT"

# Trading direction
MODE="long"  # or "short"

# Leverage (be careful!)
LEVERAGE=20

# Grid price range
START_PRICE=60000
END_PRICE=70000

# Number of grid levels
GRID_SIZE=100

# Position size per order
POSITION_SIZE_TYPE="QUOTE"  # USDT amount per order
POSITION_SIZE=10.0          # 10 USDT per order

# Risk management
ENABLE_RANGE_EXIT_RULE="True"
TAKE_PROFIT_PERCENT=5       # Exit at 5% profit
STOP_LOSS_PERCENT=2         # Exit at 2% loss
```

## 4. Run the Bot

```bash
python main.py
```

You should see output like:
```
2026-02-20 10:30:45 - __main__ - INFO - ==================================
2026-02-20 10:30:45 - __main__ - INFO - Initializing trading bot...
2026-02-20 10:30:45 - __main__ - INFO - Configuration loaded successfully.
2026-02-20 10:30:46 - src.exchange - INFO - Binance API client initialized.
2026-02-20 10:30:46 - src.bot - INFO - Setting leverage to 20x for BTCUSDT...
2026-02-20 10:30:47 - src.bot - INFO - Bot initialized successfully.
2026-02-20 10:30:47 - __main__ - INFO - Starting bot main loop...
```

## 5. Monitor the Bot

The bot logs to both console and `bot.log` file:

```bash
# Watch logs in real-time
tail -f bot.log

# Or check the log file
cat bot.log
```

## 6. Stop the Bot

Create a `.close_now` file to gracefully shutdown:

```bash
touch .close_now
```

The bot will:
- Cancel all pending orders
- Close any open positions
- Exit cleanly

## 7. Troubleshooting

### Bot won't start
- Check `.env` file exists and has correct format
- Verify API credentials are correct
- Check internet connection

### "Could not retrieve market price"
- Verify SYMBOL is correct (e.g., BTCUSDT)
- Check if Binance API is accessible
- Try with a different symbol

### Orders not filling
- Check if grid prices are reasonable
- Verify leverage is set correctly
- Check position size isn't too small
- Ensure you have enough balance

### API errors
- Check API key has Futures Trading permission
- Verify API key is for testnet (if TESTNET=True)
- Check rate limits aren't exceeded

## 8. Next Steps

1. **Test on Testnet First**: Always test with TESTNET="True"
2. **Start Small**: Use small POSITION_SIZE initially
3. **Monitor Carefully**: Watch logs and positions closely
4. **Adjust Parameters**: Fine-tune based on results
5. **Go Live**: Only switch to mainnet after successful testing

## 9. Important Notes

⚠️ **Risk Warning**:
- Grid trading can result in rapid losses
- Always use stop loss and take profit
- Never trade with funds you can't afford to lose
- Start with small position sizes
- Test thoroughly on testnet first

## 10. Key Files

- `main.py` - Entry point
- `src/bot.py` - Main bot logic
- `src/exchange.py` - Binance API wrapper
- `src/config.py` - Configuration loader
- `src/grid.py` - Grid generation
- `src/risk.py` - Risk management
- `.env` - Configuration file
- `bot.log` - Log file

## Support

For issues or questions:
1. Check `bot.log` for error messages
2. Review MIGRATION_NOTES.md for API differences
3. Check Binance API documentation: https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
