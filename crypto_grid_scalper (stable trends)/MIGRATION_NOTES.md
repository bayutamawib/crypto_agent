# Migration from Bybit to Binance

This document outlines the key changes made when converting the grid trading bot from Bybit to Binance.

## Library Changes

### Bybit Version
- **Library**: `pybit` (Bybit's official Python SDK)
- **Import**: `from pybit.unified_trading import HTTP`
- **Client**: `HTTP(testnet=True, api_key=..., api_secret=...)`

### Binance Version
- **Library**: `binance-sdk-derivatives-trading-usds-futures` (Official Binance SDK)
- **Import**: `from binance_sdk_derivatives_trading_usds_futures.derivatives_trading_usds_futures import DerivativesTradingUsdsFutures`
- **Client**: `DerivativesTradingUsdsFutures(config_rest_api=configuration)`

## Configuration Changes

### Environment Variables

**Bybit:**
```env
BYBIT_API_KEY="..."
BYBIT_API_SECRET="..."
USE_UK_ENDPOINT="False"
ACCOUNT_TYPE="UNIFIED"
```

**Binance:**
```env
BINANCE_API_KEY="..."
BINANCE_API_SECRET="..."
```

Note: Binance doesn't require UK endpoint or account type configuration in the same way.

## API Method Changes

### Set Leverage

**Bybit:**
```python
self.client.set_leverage(
    category="linear",
    symbol=symbol,
    buyLeverage=str(leverage),
    sellLeverage=str(leverage)
)
```

**Binance:**
```python
self.client.rest_api.change_initial_leverage(
    symbol=symbol,
    leverage=leverage
)
```

### Get Market Price

**Bybit:**
```python
response = self.client.get_tickers(category="linear", symbol=symbol)
mark_price = float(response['result']['list'][0]['markPrice'])
```

**Binance:**
```python
response = self.client.rest_api.mark_price(symbol=symbol)
data = response.data()
mark_price = float(data.mark_price)
```

### Get Symbol Info

**Bybit:**
```python
response = self.client.get_instruments_info(category="linear", symbol=symbol)
return response['result']['list'][0]
```

**Binance:**
```python
response = self.client.rest_api.exchange_information()
data = response.data()
for sym in data.symbols:
    if sym.symbol == symbol:
        return sym
```

### Place Order

**Bybit:**
```python
response = self.client.place_order(
    category='linear',
    symbol=symbol,
    side=bybit_side,
    orderType=bybit_order_type,
    qty=str(quantity_float),
    price=str(price),
    timeInForce='GTC'
)
```

**Binance:**
```python
response = self.client.rest_api.new_order(
    symbol=symbol,
    side=side,
    type=order_type,
    quantity=str(quantity_float),
    position_side='BOTH',
    time_in_force='GTC',
    price=str(price)
)
```

### Get Position Information

**Bybit:**
```python
response = self.client.get_positions(category="linear", symbol=symbol)
for position_data in response['result']['list']:
    if position_data['symbol'] == symbol:
        # Map response
```

**Binance:**
```python
response = self.client.rest_api.position_information_v3()
data = response.data()
for position in data:
    if position.symbol == symbol:
        # Map response
```

### Close Position

**Bybit:**
```python
response = self.client.place_order(
    category="linear",
    symbol=symbol,
    side=bybit_side,
    orderType='Market',
    qty=str(quantity),
    reduceOnly=True
)
```

**Binance:**
```python
response = self.client.rest_api.new_order(
    symbol=symbol,
    side=side,
    type='MARKET',
    quantity=str(quantity),
    position_side='BOTH',
    reduce_only=True
)
```

### Cancel All Orders

**Bybit:**
```python
response = self.client.cancel_all_orders(category="linear", symbol=symbol)
```

**Binance:**
```python
response = self.client.rest_api.cancel_all_open_orders(symbol=symbol)
```

## Response Handling

### Bybit
- Returns raw dictionaries
- Access via `response['retCode']`, `response['result']`
- Manual error checking required

### Binance
- Returns response objects with `.data()` method
- Access via `response.data()` returns typed objects
- Built-in error handling with specific exception types
- Rate limits available via `response.rate_limits`

## Key Differences

| Aspect | Bybit | Binance |
|--------|-------|---------|
| **Leverage** | Set with order parameters | Must set separately before order |
| **Position Mode** | Implicit in unified account | Explicit BOTH/LONG/SHORT |
| **Batch Orders** | Single order at a time | Supports batch via `place_multiple_orders()` |
| **Response Type** | Raw dictionaries | Typed objects with `.data()` |
| **Error Handling** | Manual checking | Exception-based |
| **Rate Limits** | Not directly exposed | Available in response |
| **Testnet** | Separate endpoint parameter | Separate base_path in config |

## Testing

Both versions have been tested with:
- Grid generation and placement
- Position tracking
- Exit condition checking
- Order cancellation
- Position closing

Test on Binance Testnet before running on mainnet:
1. Create account at https://testnet.binancefuture.com
2. Generate API keys
3. Set `TESTNET="True"` in `.env`
4. Run bot with small position sizes

## Performance Considerations

- Binance SDK uses official library (more stable)
- Response objects are more structured (easier to debug)
- Batch order support available for future optimization
- Rate limiting is more transparent

## Future Enhancements

Potential improvements for Binance version:
1. Use `place_multiple_orders()` for batch grid placement
2. Implement WebSocket streams for real-time price updates
3. Add order modification support
4. Implement trailing stop losses
5. Add performance metrics and statistics
