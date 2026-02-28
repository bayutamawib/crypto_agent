# Crypto Grid Scalper - Binance Edition

A Python-based grid trading bot for Binance Futures (USDT-M) that automatically places and manages grid orders for scalping strategies.

## Features

- **Grid Trading**: Automatically generates and places limit orders across a price range
- **Risk Management**: Built-in stop loss, take profit, and position exit rules
- **Leverage Support**: Configurable leverage for increased position sizing
- **Testnet Support**: Test your strategy on Binance Testnet before live trading
- **Flexible Position Sizing**: Support for both BASE and QUOTE position sizing
- **Exit Rules**: 
  - Stop Loss percentage-based exits
  - Take Profit percentage-based exits
  - 75% Range Exit Rule
  - 3-Position Rule (exit after 3 consecutive positions)

## Installation

### Prerequisites
- Python 3.9+
- Binance API credentials (Testnet or Mainnet)

### Setup

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example.txt .env
```

4. Edit `.env` with your Binance API credentials and trading parameters

## Configuration

Edit `.env` file with your settings:

```env
# Binance API Credentials
BINANCE_API_KEY="your_api_key"
BINANCE_API_SECRET="your_api_secret"

# Trading Parameters
MODE="long"                    # "long", "short", or "neutral"
SYMBOL="BTCUSDT"              # Trading pair
LEVERAGE=20                   # Leverage multiplier
START_PRICE=60000             # Grid lower bound
END_PRICE=70000               # Grid upper bound
GRID_SIZE=100                 # Number of grid levels
POSITION_SIZE_TYPE="QUOTE"    # "QUOTE" or "BASE"
POSITION_SIZE=10.0            # Position size in USDT or base asset
ENABLE_RANGE_EXIT_RULE="True" # Enable range exit rule
RANGE_EXIT_THRESHOLD_PERCENT=100  # Threshold percentage for range exit (default 100%)
TP_MODE="PERCENTAGE"          # "PERCENTAGE" or "GRID_RANGE"
TAKE_PROFIT_PERCENT=5         # Take profit percentage (used if TP_MODE="PERCENTAGE")
STOP_LOSS_PERCENT=2           # Stop loss percentage (always percentage-based)
TESTNET="True"                # Use testnet (True) or mainnet (False)
DUAL_SIDE_POSITION="False"    # Enable hedge mode (True) or one-way mode (False)

# Grid Position Reopening Logic
ENABLE_POSITION_REOPEN="True"           # Enable/disable automatic position reopening
MAX_CONSECUTIVE_GRID_POSITIONS=3        # Max consecutive positions before reset (or "unlimited")

# Market Position Logic Configuration (Volatility Detector Integration)
ENABLE_MARKET_POSITION_LOGIC="True"     # Enable/disable market position logic
ANALYSIS_INTERVAL_MINUTES=10            # How often to run Volatility Detector analysis
VOLATILITY_DETECTOR_MAX_RETRIES=3       # Max retry attempts if analysis fails
VOLATILITY_DETECTOR_PATH="../Volatility_Detector_Crypto"  # Path to Volatility Detector
MAX_MARKET_POSITION_REOPENS="unlimited" # Max market position reopens per signal (or "unlimited")
```

### Take Profit Modes

**PERCENTAGE Mode:**
- Closes position when profit reaches the specified percentage
- Example: Entry at $100, TP at 5% closes at $105 (LONG) or $95 (SHORT)

**GRID_RANGE Mode:**
- Closes position when price reaches the next grid level
- Example: Entry at $100, next grid level at $103 closes at $103 (LONG) or $97 (SHORT)
- More frequent exits with smaller profits per trade
- Aligns exits with grid structure

**Stop Loss:**
- Always percentage-based regardless of TP_MODE
- Example: Entry at $100, SL at 2% closes at $98 (LONG) or $102 (SHORT)

### Range Exit Rule Configuration

The Range Exit Rule closes all positions and resets the grid when price moves beyond a configured threshold from the grid boundaries.

**Configuration:**
```env
ENABLE_RANGE_EXIT_RULE="True"           # Enable/disable the rule
RANGE_EXIT_THRESHOLD_PERCENT=100        # Threshold percentage (default 100%)
```

**How It Works:**
```
Grid Setup:
- START_PRICE = 60000, END_PRICE = 70000
- Grid_Width = 10000
- Grid_Center = 65000 (current price when grid generated)
- Grid_Lower = 60000, Grid_Upper = 70000

With RANGE_EXIT_THRESHOLD_PERCENT=100:
- Exit_Threshold = Grid_Width × (100/100) = 10000
- Lower_Exit_Price = 60000 - 10000 = 50000
- Upper_Exit_Price = 70000 + 10000 = 80000
- Trigger: Price < 50000 OR Price > 80000

With RANGE_EXIT_THRESHOLD_PERCENT=75:
- Exit_Threshold = Grid_Width × (75/100) = 7500
- Lower_Exit_Price = 60000 - 7500 = 52500
- Upper_Exit_Price = 70000 + 7500 = 77500
- Trigger: Price < 52500 OR Price > 77500
```

**Threshold Interpretation:**
- **100%** (default): Exit when price moves one full grid width beyond boundaries
- **75%**: Exit when price moves 75% of grid width beyond boundaries
- **150%**: Exit when price moves 1.5x grid width beyond boundaries
- Higher values = more lenient (positions stay open longer)
- Lower values = stricter (positions close sooner)

## Usage

### Running the Bot

```bash
python main.py
```

The bot will:
1. Load configuration from `.env`
2. Connect to Binance API
3. Set leverage for the trading pair
4. Generate grid levels centered at current market price
5. Place limit orders at each grid level
6. Monitor positions and exit conditions
7. Reset grid when exit conditions are triggered

### Stopping the Bot

Create a `.close_now` file in the bot directory to gracefully shutdown:

```bash
touch .close_now
```

The bot will:
1. Cancel all open orders
2. Close any open positions
3. Exit cleanly

## How It Works

## How It Works

### Grid Generation
- Grid is centered at the current market price
- Grid levels are evenly spaced between START_PRICE and END_PRICE
- For LONG mode: BUY orders placed below current price
- For SHORT mode: SELL orders placed above current price
- For NEUTRAL mode: Both BUY and SELL orders placed

### Position Opening Conditions

**Grid Positions Open When:**
1. **Limit order fills** - Market price touches a grid level with a pending limit order
   - Entry price = grid level price
   - Position counter increments
   - TP/SL targets calculated

2. **Position reopening** - After a grid position closes, a new limit order is placed at the same grid level
   - Only if `ENABLE_POSITION_REOPEN="True"`
   - Happens automatically in next bot cycle
   - Allows unlimited grid levels in neutral mode

**Market Positions Open When:**
1. **UPTREND + OVERBOUGHT** - Volatility Detector signal triggers
   - Opens LONG market position at current price
   - Resets reopens counter to 0

2. **DOWNTREND + OVERSOLD** - Volatility Detector signal triggers
   - Opens SHORT market position at current price
   - Resets reopens counter to 0

3. **Same signal continues** - If previous signal was valid
   - Continues current trade (no new position)
   - Reopens counter unchanged

### Position Closing Conditions

**Grid Positions Close Due To:**

1. **TP/SL Targets Hit** (custom position targets)
   - LONG: Price >= Entry × (1 + TP%) OR Price <= Entry × (1 - SL%)
   - SHORT: Price <= Entry × (1 - TP%) OR Price >= Entry × (1 + SL%)
   - Action: Close position with market order
   - Grid remains active (can open new positions)

2. **Stop Loss Triggered** (risk manager)
   - LONG: Price <= Entry × (1 - SL%)
   - SHORT: Price >= Entry × (1 + SL%)
   - Action: Cancel all orders, close position, reset grid

3. **Take Profit Triggered** (risk manager)
   - LONG: Price >= Entry × (1 + TP%)
   - SHORT: Price <= Entry × (1 - TP%)
   - Action: Cancel all orders, close position, reset grid

4. **Range Exit Rule Triggered** (configurable threshold)
   - Price moves beyond grid boundaries by configured percentage
   - Default: 100% (one full grid width)
   - Action: Cancel all orders, close position, reset grid

5. **Max Consecutive Positions Reached** (configurable, default 3)
   - Position counter >= MAX_CONSECUTIVE_GRID_POSITIONS
   - Action: Cancel all orders, close position, reset grid

6. **Manual Shutdown** (.close_now file)
   - Action: Cancel all orders, close position, exit bot

**Market Positions Close Due To:**

1. **TP/SL Targets Hit** - Same as grid positions
   - If trend still valid (not NEUTRAL): Immediately reopen
   - If trend is NEUTRAL: Close and do NOT reopen

2. **Stop Loss Triggered** - Same as grid positions
   - Closes position, resets grid

3. **Take Profit Triggered** - Same as grid positions
   - Closes position, resets grid

4. **Range Exit Rule Triggered** - Same as grid positions
   - Closes position, resets grid

5. **NEUTRAL Momentum Detected** - Volatility Detector shows NEUTRAL
   - Closes market position
   - Does NOT reopen
   - Resets reopens counter to 0

6. **Manual Shutdown** - Same as grid positions
   - Closes position, exits bot

### Position Counter

The position counter tracks consecutive grid positions opened without a full grid reset.

**Behavior:**
- Increments by 1 each time a new grid position opens
- Resets to 0 when grid resets (due to exit conditions)
- Used to enforce MAX_CONSECUTIVE_GRID_POSITIONS limit
- Does NOT affect market positions

**Example:**
```
Position 1 opens → counter = 1
Position 2 opens → counter = 2
Position 3 opens → counter = 3
Max reached (3) → Grid resets → counter = 0
Position 1 opens (new grid) → counter = 1
```

### Market Position Reopening

When a market position hits TP or SL:
1. Position closes
2. Check if trend is still valid (not NEUTRAL):
   - If YES: Immediately reopen same position type at current market price
   - If NO: Position closes and does NOT reopen
3. Increment reopens counter (only if reopened)
4. Check if reopens limit reached:
   - If YES: Position closes and does NOT reopen again
   - If NO: Continue reopening on future TP/SL hits

**Reopens Counter:**
- Tracks reopens for current signal
- Resets to 0 when signal changes
- Resets to 0 when NEUTRAL detected
- Respects MAX_MARKET_POSITION_REOPENS limit

### Exit Process (Grid Reset)

When any major exit condition triggers:
1. Cancel all pending limit orders
2. Close any open market position
3. Clear position reopening queue
4. Reset position counter to 0
5. Mark grid as inactive
6. Generate new grid at current price on next cycle

## Position Management

### Grid Position Reopening Logic (Neutral Grid Mode)

### Overview
When trading in NEUTRAL mode with dual-side positions, Bybit's API behavior closes BOTH long and short positions when closing ANY position. This limits traditional grid trading to only 2 grid levels (1 buy, 1 sell).

The Position Reopening feature solves this by automatically reopening positions at the same grid level after they close, enabling unlimited grid levels with continuous position shifting and average price adjustment.

### How It Works

**Enabled by default:** `ENABLE_POSITION_REOPEN="True"` in `.env`

When a grid position closes:
1. Bot detects the position closure
2. Determines the opposite side (if LONG closed → reopen SHORT, if SHORT closed → reopen LONG)
3. Adds position to reopen queue with:
   - Same grid level price
   - Same quantity
   - Opposite side
   - Correct position index for Bybit API
4. Next bot cycle places new limit order at the same grid level
5. Process repeats, creating continuous grid trading with average price shifts

### Configuration

```env
# Enable/disable position reopening
ENABLE_POSITION_REOPEN="True"

# Maximum consecutive positions before grid reset
MAX_CONSECUTIVE_GRID_POSITIONS=3
# Options:
#   3, 5, 10, etc. (numeric limit)
#   "unlimited" (never close due to position count)
```

### Max Consecutive Positions Rule

Controls how many consecutive positions can be opened before the grid resets.

**Default (3):**
```
Position 1 opens → Position 2 opens → Position 3 opens → Grid resets
```

**With "unlimited":**
```
Positions keep opening indefinitely until:
- TP/SL hit
- Stop Loss triggered
- Take Profit triggered
- Range Exit Rule triggered
- Manual shutdown (.close_now file)
```

### Example Workflow

```
Grid Levels: [0.134, 0.135, 0.136, 0.137, 0.138]
MAX_CONSECUTIVE_GRID_POSITIONS=3

Cycle 1:
  - BUY order fills at 0.134 (LONG position opens) → counter = 1
  - Price rises to 0.135
  - SELL order fills at 0.135 (SHORT position opens) → counter = 2
  - Price drops to 0.134
  - LONG position closes (profit taken)
  → Reopen queue: [SELL at 0.134]

Cycle 2:
  - New SELL order placed at 0.134 (SHORT position reopens) → counter = 3
  - Price continues trading
  - BUY order fills at 0.133 (LONG position opens) → counter = 4
  → Grid reset triggered! (counter >= 3)
  → Cancel all orders, close positions, reset counter to 0
```

### Benefits

- Unlimited grid levels (not limited to 2)
- Continuous position shifting for better average prices
- Increased trading frequency and opportunities
- Works seamlessly with existing grid logic
- Automatic queue management
- Configurable limits for different strategies

### Limitations

- Only works with NEUTRAL mode and dual-side positions
- Requires careful position sizing to avoid excessive leverage
- Works best with stable price ranges

## Market Position Logic (Volatility Detector Integration)

### Overview
The bot can integrate with Volatility_Detector_Crypto to open/close market positions based on trend and momentum analysis. This runs independently from grid trading, allowing simultaneous grid and market position trading.

### How It Works

**Enabled by default:** `ENABLE_MARKET_POSITION_LOGIC="True"` in `.env`

Every N minutes (configurable, default 10):
1. Runs Volatility Detector analysis for the trading symbol
2. Extracts trend (UPTREND/DOWNTREND) and momentum (OVERBOUGHT/OVERSOLD/NEUTRAL)
3. Compares with previous result (if same, continues current trade)
4. Opens/closes market positions based on conditions:

**Condition 1: UPTREND + OVERBOUGHT**
- Close any existing market position
- Open LONG market position at current price
- Set TP/SL targets
- Reset reopens counter to 0

**Condition 2: DOWNTREND + OVERSOLD**
- Close any existing market position
- Open SHORT market position at current price
- Set TP/SL targets
- Reset reopens counter to 0

**Condition 3: NEUTRAL momentum**
- Close current market position (if any)
- Do NOT open new position
- Reset reopens counter to 0

**Condition 4: Same as previous result**
- Continue current trade (no action)
- Keep reopens counter unchanged

### Market Position Reopening on TP/SL

When a market position hits TP or SL:
1. Position closes
2. Check if trend is still valid (not NEUTRAL):
   - If YES: Immediately reopen same position type at current market price
   - If NO: Position closes and does NOT reopen
3. Increment reopens counter (only if reopened)
4. Check if reopens limit reached:
   - If YES: Position closes and does NOT reopen again
   - If NO: Continue reopening on future TP/SL hits

**Example Workflow:**
```
Signal: UPTREND + OVERBOUGHT → Open LONG at $100

Cycle 1:
  - LONG position at $100
  - TP at $105 (5% profit)
  - Price rises to $105
  - TP triggered → Close LONG
  - Trend still UPTREND (not NEUTRAL)
  → Reopen LONG at $105 (reopens = 1)

Cycle 2:
  - LONG position at $105
  - TP at $110.25
  - Price rises to $110.25
  - TP triggered → Close LONG
  - Trend still UPTREND
  → Reopen LONG at $110.25 (reopens = 2)

Cycle 3:
  - LONG position at $110.25
  - SL at $108.05
  - Price drops to $108.05
  - SL triggered → Close LONG
  - Trend still UPTREND
  → Reopen LONG at $108.05 (reopens = 3)

... (continues until MAX_MARKET_POSITION_REOPENS reached or NEUTRAL detected)

When NEUTRAL detected:
  - Close current LONG position
  - Do NOT reopen
  - Reset reopens counter to 0
  - Wait for next valid signal (UPTREND+OVERBOUGHT or DOWNTREND+OVERSOLD)
```

### Configuration

```env
# Enable/disable market position logic
ENABLE_MARKET_POSITION_LOGIC="True"

# Analysis interval in minutes (how often to run Volatility Detector)
ANALYSIS_INTERVAL_MINUTES=10

# Maximum retry attempts if analysis fails
VOLATILITY_DETECTOR_MAX_RETRIES=3

# Path to Volatility Detector directory
VOLATILITY_DETECTOR_PATH="../Volatility_Detector_Crypto"

# Maximum market position reopens per signal
MAX_MARKET_POSITION_REOPENS="unlimited"
# Options:
#   5, 10, 20, etc. (numeric limit - reopen up to N times per signal)
#   "unlimited" (reopen indefinitely until NEUTRAL detected, default)
```

### Position Types & Differences

**Grid Positions:**
- Opened by: Limit orders at grid levels
- Closed by: TP/SL targets, Stop Loss, Take Profit, Range Exit Rule, Max Consecutive Positions
- Reopening: Automatic at same grid level after closure (if enabled)
- Limit: MAX_CONSECUTIVE_GRID_POSITIONS (default 3 or "unlimited")
- Affected by: NEUTRAL momentum? NO
- Quantity: POSITION_SIZE (configurable)
- Leverage: LEVERAGE (configurable)

**Market Positions:**
- Opened by: Market order based on Volatility Detector signal
- Closed by: TP/SL targets, Stop Loss, Take Profit, Range Exit Rule, NEUTRAL momentum
- Reopening: Automatic on TP/SL if trend still valid
- Limit: MAX_MARKET_POSITION_REOPENS (default "unlimited")
- Affected by: NEUTRAL momentum? YES (closes position)
- Quantity: POSITION_SIZE (same as grid)
- Leverage: LEVERAGE (same as grid)

### Signal Change Detection

When Volatility Detector signal changes (e.g., UPTREND+OVERBOUGHT → DOWNTREND+OVERSOLD):
1. Current market position closes
2. Reopens counter resets to 0
3. New position opens with new signal
4. Reopens counter starts fresh for new signal

This ensures each signal gets its own reopens budget.

### Error Handling

If Volatility Detector analysis fails:
1. Retry up to 3 times (configurable via VOLATILITY_DETECTOR_MAX_RETRIES)
2. Wait 5 seconds between retries
3. If all retries fail, skip this analysis session
4. Try again in N minutes (next analysis interval)
5. All errors logged to `bot.log` for debugging

**Common Issues:**
- JSON parsing errors: Ensure Volatility Detector is outputting clean JSON with `--json` flag
- Timeout errors: Increase VOLATILITY_DETECTOR_MAX_RETRIES or check system resources
- Path errors: Verify VOLATILITY_DETECTOR_PATH points to correct directory

## Logging

Bot logs are written to `bot.log` and console output. Log levels:
- INFO: Normal operation events
- WARNING: Exit triggers and important events
- ERROR: API errors and exceptions
- DEBUG: Detailed operation information

## API Requirements

Binance API key must have these permissions:
- Futures Trading (Read + Write)
- Position Management
- Order Management

## Testnet

To test on Binance Testnet:
1. Create testnet account at https://testnet.binancefuture.com
2. Generate testnet API keys
3. Set `TESTNET="True"` in `.env`

## Risk Disclaimer

Grid trading involves significant risk. This bot:
- Can result in rapid losses
- Requires proper risk management configuration
- Should be tested thoroughly on testnet first
- Should never be run with funds you cannot afford to lose

Always start with small position sizes and thoroughly test your strategy.

## Troubleshooting

### "API key and secret must be provided"
- Check `.env` file has BINANCE_API_KEY and BINANCE_API_SECRET
- Ensure no extra spaces or quotes

### "Could not retrieve market price"
- Check internet connection
- Verify API credentials are valid
- Check if symbol is correct (e.g., BTCUSDT)

### Orders not filling
- Check if leverage is set correctly
- Verify position size is not too small
- Check if grid prices are reasonable for current market

