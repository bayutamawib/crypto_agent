# Bybit Take Profit API Migration

## Overview
Migrated from custom Python-based take profit checking to Bybit's native API `set_trading_stop` method for take profit management.

## Changes Made

### 1. Exchange API Method (src/exchange.py)

**Added new method: `set_take_profit()`**

```python
def set_take_profit(self, symbol, tp_price, position_side='BOTH'):
    """
    Sets take profit for an open position using Bybit API.
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        tp_price (float): Take profit price
        position_side (str): 'LONG', 'SHORT', or 'BOTH'
    
    Returns:
        bool: True if successful, False otherwise
    """
```

**Implementation Details:**
- Uses Bybit's `set_trading_stop()` API method
- Maps position_side to Bybit's positionIdx:
  - 'LONG' → '0'
  - 'SHORT' → '1'
  - 'BOTH' → '2' (one-way mode)
- Logs all API calls and responses
- Returns True/False for success/failure

### 2. Grid Position TP Management (src/bot.py)

**Updated: Position opening logic**

When a grid position opens:
1. Calculate TP price (same as before)
2. **NEW:** Call `exchange.set_take_profit()` to set TP via Bybit API
3. Store TP price in `position_targets` for reference

```python
# Set take profit via Bybit API
if 'tp_price' in self.position_targets:
    tp_price = self.position_targets['tp_price']
    self.exchange.set_take_profit(
        symbol=self.config['symbol'],
        tp_price=tp_price,
        position_side=position_side
    )
```

**Updated: TP/SL checking logic**

Modified `check_tp_sl_targets()` method:
- **REMOVED:** Custom TP price checking
- **KEPT:** Custom SL price checking (still needed)
- Now only checks stop loss, TP is handled by Bybit API

```python
def check_tp_sl_targets(self, current_price):
    """
    Checks if current price hits stop loss target.
    Take profit is now handled by Bybit API, so we only check stop loss here.
    """
    # Only check SL, TP is handled by Bybit API
```

### 3. Market Position TP Management (src/market_position_manager.py)

**Updated: Market position opening logic**

When a market position opens:
1. Calculate TP price (same as before)
2. **NEW:** Call `exchange.set_take_profit()` to set TP via Bybit API
3. Store TP price in `market_position_targets` for reference

```python
# Set take profit via Bybit API
if 'tp_price' in self.market_position_targets:
    tp_price = self.market_position_targets['tp_price']
    position_side = 'LONG' if side == 'BUY' else 'SHORT'
    self.exchange.set_take_profit(
        symbol=symbol,
        tp_price=tp_price,
        position_side=position_side
    )
```

**Updated: TP/SL checking logic**

Modified `check_market_position_tp_sl()` method:
- **REMOVED:** Custom TP/SL price checking
- **NEW:** Detects position closure by checking if position size = 0
- Assumes closure was due to TP (since we set TP via API)

```python
def check_market_position_tp_sl(self, current_price: Decimal) -> Optional[str]:
    """
    Checks if market position was closed by Bybit API (TP/SL).
    Since TP is now handled by Bybit API, we detect closure by checking if position is gone.
    """
    # If position is closed (size = 0), it was closed by API (TP or SL)
    if not position_info or float(position_info.get('positionAmt', 0)) == 0:
        return 'TAKE_PROFIT'
```

## Benefits

1. **Bybit Handles TP Execution:** More reliable, no network latency issues
2. **Reduced Bot Load:** Bot no longer needs to constantly check TP prices
3. **Faster Execution:** Bybit's server-side TP execution is faster than polling
4. **Cleaner Code:** Separation of concerns - API handles TP, bot handles SL
5. **Better Precision:** Bybit's TP execution is more precise than price polling

## Stop Loss Handling

**Stop Loss is still handled by custom Python code:**
- Bot continues to check SL prices every cycle
- When SL is triggered, bot closes position immediately
- This allows for more flexible SL logic (e.g., trailing stops in future)

## Configuration

No configuration changes needed. Existing `.env` variables work as before:
- `TAKE_PROFIT_PERCENT` - TP percentage (used to calculate TP price)
- `STOP_LOSS_PERCENT` - SL percentage (still checked by bot)
- `TP_MODE` - PERCENTAGE or GRID_RANGE (used to calculate TP price)

## Testing Checklist

- [ ] Grid positions open and TP is set via API
- [ ] Market positions open and TP is set via API
- [ ] Position closes when TP is hit (Bybit API closes it)
- [ ] Bot detects position closure and handles reopening
- [ ] Stop loss still works (bot checks and closes)
- [ ] Position reopening works after TP hit
- [ ] Signal changes reset reopens counter
- [ ] NEUTRAL momentum closes position

## Bybit API Reference

**Method:** `set_trading_stop()`

**Parameters:**
- `category`: 'linear' (futures)
- `symbol`: Trading pair (e.g., 'BTCUSDT')
- `positionIdx`: Position index (0=LONG, 1=SHORT, 2=BOTH)
- `takeProfit`: TP price (string)

**Response:**
- `retCode`: 0 = success, non-zero = error
- `retMsg`: Error message if failed
- `result`: Response data if successful

## Troubleshooting

### TP not being set
- Check API logs for `set_trading_stop` calls
- Verify position_side is correct (LONG/SHORT/BOTH)
- Ensure TP price is valid (not too close to entry)

### Position not closing on TP
- Check Bybit API status
- Verify TP price was set correctly
- Check bot logs for position closure detection

### Bot not detecting TP closure
- Ensure `check_market_position_tp_sl()` is being called
- Check if position size is actually 0 after TP hit
- Review bot logs for position information queries

## Future Enhancements

1. Add Bybit SL API support (currently using custom checking)
2. Add trailing stop support via Bybit API
3. Add TP modification logic (update TP if conditions change)
4. Add TP cancellation logic (remove TP if position closes early)
