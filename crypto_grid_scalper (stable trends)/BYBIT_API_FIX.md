# Bybit API Fix - Side Parameter Issue

## Problem
The bot was throwing "Side invalid (ErrCode: 10001)" errors when trying to create orders on Bybit.

### Error Message
```
Side invalid (ErrCode: 10001)
Request → POST https://api.bybit.com/v5/order/create: 
{"category": "linear", "symbol": "BANUSDT", "side": "BUY", ...}
```

## Root Cause
Bybit API requires side values to be capitalized as "Buy" and "Sell", not "BUY" and "SELL".

## Solution
Updated `src/exchange.py` to normalize side values before sending to Bybit API:

### Changes Made

#### 1. `create_order()` method
- Added side normalization: `'BUY'` → `'Buy'`, `'SELL'` → `'Sell'`
- Ensures all order creation requests use correct Bybit format

#### 2. `close_position_market()` method
- Added side normalization for market close orders
- Ensures position closing uses correct format

#### 3. `close_all_positions()` method
- Updated to use correct Bybit side format ('Buy'/'Sell')
- Ensures all position closing operations work correctly

## Code Changes

### Before
```python
params = {
    'category': 'linear',
    'symbol': symbol,
    'side': side,  # 'BUY' or 'SELL' - WRONG for Bybit
    'orderType': order_type,
    ...
}
```

### After
```python
# Normalize side to Bybit format (Buy/Sell)
bybit_side = 'Buy' if side.upper() == 'BUY' else 'Sell' if side.upper() == 'SELL' else side

params = {
    'category': 'linear',
    'symbol': symbol,
    'side': bybit_side,  # 'Buy' or 'Sell' - CORRECT for Bybit
    'orderType': order_type,
    ...
}
```

## Bybit API Requirements
According to [Bybit API Documentation](https://bybit-exchange.github.io/docs/v5/order/create-order):
- **Side**: "Buy" or "Sell" (case-sensitive, capitalized)
- **OrderType**: "Limit" or "Market" (case-sensitive, capitalized)
- **TimeInForce**: "GTC", "IOC", "FOK", "PostOnly" (for Limit orders)

## Testing
After this fix:
1. Orders should be created successfully with proper side values
2. Position closing should work correctly
3. All grid orders should place without "Side invalid" errors

## Files Modified
- `src/exchange.py` - Added side normalization in 3 methods

## Status
✅ Fix applied
✅ No syntax errors
✅ Ready for testing
