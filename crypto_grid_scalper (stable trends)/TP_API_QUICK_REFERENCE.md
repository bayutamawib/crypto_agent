# Take Profit API - Quick Reference

## What Changed?

**Before:** Bot checked TP price every cycle and closed position manually
**After:** Bybit API handles TP execution, bot only detects closure

## How It Works Now

### Grid Positions
```
1. Position opens (limit order fills)
2. Bot calculates TP price
3. Bot calls exchange.set_take_profit() → Bybit API sets TP
4. Bybit monitors price and closes position when TP hit
5. Bot detects closure and handles reopening
```

### Market Positions
```
1. Position opens (market order)
2. Bot calculates TP price
3. Bot calls exchange.set_take_profit() → Bybit API sets TP
4. Bybit monitors price and closes position when TP hit
5. Bot detects closure and handles reopening
```

## Key Methods

### Exchange API
```python
exchange.set_take_profit(
    symbol='BTCUSDT',
    tp_price=45000.50,
    position_side='LONG'  # or 'SHORT' or 'BOTH'
)
```

### Bot TP Checking
```python
# Now only checks SL (TP is handled by Bybit)
tp_sl_trigger = self.check_tp_sl_targets(current_price)
# Returns: 'STOP_LOSS' or None (TP is not checked here anymore)
```

### Market Position TP Checking
```python
# Detects if position was closed by Bybit API
tp_sl_trigger = self.market_position_manager.check_market_position_tp_sl(current_price)
# Returns: 'TAKE_PROFIT' if position is gone, None otherwise
```

## Configuration

No changes needed! Use existing variables:
- `TAKE_PROFIT_PERCENT=5` - TP is 5% above entry
- `TP_MODE=PERCENTAGE` - Use percentage mode
- `STOP_LOSS_PERCENT=2` - SL is still checked by bot

## Logs to Look For

### When TP is set
```
Setting take profit for BTCUSDT (side: LONG): TP=45000.50
Take profit set successfully for BTCUSDT: {...}
```

### When position closes (TP hit)
```
Market position closed by Bybit API (likely TP triggered)
```

### When bot detects closure
```
Position closure detected! Adding to reopen queue.
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| TP not being set | Check API logs, verify position_side is correct |
| Position not closing | Check Bybit API status, verify TP price is valid |
| Bot not detecting closure | Check if position size is 0, review logs |
| TP price seems wrong | Verify calculation: Entry × (1 + TP%) for LONG |

## Stop Loss

**Still handled by bot (not changed):**
- Bot checks SL price every cycle
- When SL hit, bot closes position immediately
- Allows for flexible SL logic in future

## Position Reopening

**Works the same as before:**
- After TP hit, position closes
- If trend still valid, bot reopens immediately
- Respects MAX_MARKET_POSITION_REOPENS limit

## Testing

Quick test to verify TP is working:
1. Open position manually or via bot
2. Check Bybit API logs for `set_trading_stop` call
3. Verify TP price is set correctly
4. Wait for price to hit TP
5. Verify position closes automatically
6. Check bot logs for closure detection

## API Reference

**Bybit Method:** `set_trading_stop()`

**Parameters:**
- `category`: 'linear'
- `symbol`: 'BTCUSDT'
- `positionIdx`: '0' (LONG), '1' (SHORT), '2' (BOTH)
- `takeProfit`: '45000.50'

**Success Response:**
```
retCode: 0
retMsg: 'OK'
result: {...}
```

**Error Response:**
```
retCode: 110001
retMsg: 'Invalid position'
```
