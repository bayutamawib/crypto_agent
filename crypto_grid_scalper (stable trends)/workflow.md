Here's the complete data flow for exchange.py:


.env file
   ↓
config.py (load_config() reads .env)
   ↓
main.py (calls load_config() and passes to Bot)
   ↓
bot.py (receives config, passes API credentials to Exchange)
   ↓
exchange.py (receives api_key, api_secret, testnet from bot.py)
   ↓
Binance API (exchange.py uses these to connect and execute orders)


Specifically for exchange.py:

1. Gets api_key and api_secret from bot.py (which got them from config)
2. Gets testnet flag from bot.py (which got it from config)
3. Config comes from .env file via config.py
4. hen methods like place_stop_loss_order() are called, they receive parameters from bot.py (entry_price, stop_loss_percent, mode, etc.)
5. Those parameters ultimately come from .env (STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT, MODE, etc.)
So the chain is: .env → config.py → main.py → bot.py → exchange.py → Binance API