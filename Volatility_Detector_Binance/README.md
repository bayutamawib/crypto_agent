# Volatility Detector - Binance Version

A cryptocurrency volatility detection system using Binance API. Analyzes technical indicators (SMA, Stochastic K, ATR, Bollinger Bands) to identify market trends and momentum.

## Features

- **Binance API Integration** - Real-time market data from Binance
- **Technical Analysis** - SMA, Stochastic K, ATR, Bollinger Bands
- **Trend Detection** - UPTREND/DOWNTREND based on SMA(9) vs SMA(26)
- **Momentum Analysis** - OVERBOUGHT/OVERSOLD/NEUTRAL based on Stochastic K
- **Single Ticker Analysis** - Detailed analysis for specific cryptocurrencies
- **JSON Output** - Programmatic output for integration with trading bots

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Binance API credentials in `.env`:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=false
```

## Usage

### Single Ticker Analysis

Analyze a specific cryptocurrency:

```bash
# Display analysis in human-readable format
python -m src.bot.analyze_ticker BTCUSDT

# Output as JSON (for bot integration)
python -m src.bot.analyze_ticker BTCUSDT --json

# Specify custom interval and limit
python -m src.bot.analyze_ticker ETHUSDT 5m 100
```

### Configuration

Edit `.env` to customize:

```
# Technical Indicators
STOCH_K_PERIOD=7              # Stochastic K period
STOCH_K_SMOOTHING=3           # Stochastic smoothing period

# Single Ticker Analysis
SINGLE_TICKER_INTERVAL=1m     # Candle interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
SINGLE_TICKER_LIMIT=200       # Number of candles to fetch
```

## Technical Indicators

### SMA (Simple Moving Average)
- **Periods**: 9, 12, 26
- **Purpose**: Trend identification
- **Calculation**: Average of closing prices over N periods

### Stochastic K
- **Period**: 7 (configurable)
- **Smoothing**: 3
- **Range**: 0-100
- **Interpretation**:
  - < 20: OVERSOLD (potential buy)
  - > 80: OVERBOUGHT (potential sell)
  - 20-80: NEUTRAL

### ATR (Average True Range)
- **Period**: 14
- **Purpose**: Volatility measurement

### Bollinger Bands
- **Period**: 20
- **Purpose**: Support/resistance levels

## Output Format

### JSON Output Example

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

### Trend & Momentum Combinations

| Trend | Momentum | Signal |
|-------|----------|--------|
| UPTREND | OVERBOUGHT | Strong Buy |
| DOWNTREND | OVERSOLD | Strong Sell |
| Any | NEUTRAL | Neutral |

## Integration with Trading Bots

The Binance version can be integrated with trading bots by:

1. Running analysis with `--json` flag
2. Parsing the JSON output
3. Using trend and momentum signals for trading decisions

Example:
```bash
python -m src.bot.analyze_ticker BTCUSDT --json | jq '.momentum'
```

## Differences from Bybit Version

- Uses `python-binance` library instead of `pybit`
- Binance interval format: `1m`, `5m`, `15m`, `1h`, etc. (vs Bybit: `1`, `5`, `15`, `60`)
- Binance spot market data (vs Bybit: linear/inverse futures)
- No mark price or index price for spot market (uses last price)

## Troubleshooting

### API Connection Issues
- Verify API credentials in `.env`
- Check if testnet is enabled/disabled correctly
- Ensure API key has appropriate permissions

### Insufficient Data
- Increase `SINGLE_TICKER_LIMIT` to fetch more candles
- Ensure symbol exists on Binance (e.g., BTCUSDT)

### Calculation Errors
- Ensure at least 26 candles are available for SMA(26)
- Check that OHLCV data is valid

## Requirements

- Python 3.8+
- python-binance
- pandas
- numpy
- ta (technical analysis library)
- python-dotenv
