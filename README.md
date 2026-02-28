# Grid Scalper: Position Opening & Closing Conditions

## Overview
The Grid Scalper bot operates in a continuous cycle of opening and closing positions based on grid orders and multiple exit conditions. Here's the complete conditional logic:

---

## POSITION OPENING CONDITIONS

### When Positions Open

Positions open **automatically** when limit orders from the grid are filled by market price movement.

#### 1. Grid Order Placement (Initial Setup)

**Condition:** `if not self.is_grid_active`
- Bot generates a new grid centered at current market price
- Places limit orders at each grid level
- Sets `is_grid_active = True`

**Grid Level Filtering by Mode:**

```
LONG MODE (Dual-Side):
├─ Only place BUY orders below current price
└─ Condition: level_price < current_price

SHORT MODE (Dual-Side):
├─ Only place SELL orders above current price
└─ Condition: level_price > current_price

NEUTRAL MODE (Dual-Side):
├─ Place BUY orders below current price
├─ Place SELL orders above current price
└─ Condition: level_price < current_price OR level_price > current_price

ONE-WAY MODE (same logic, but position_side = 'BOTH'):
├─ LONG: BUY orders only below current price
├─ SHORT: SELL orders only above current price
└─ NEUTRAL: Both BUY and SELL orders
```

#### 2. Order Execution

**Condition:** Market price touches a grid level with a pending limit order
- Limit order fills automatically
- Position opens at that grid level price
- Entry price = grid level price

#### 3. Position Detection

**Condition:** `if self.open_positions` (position_amt != 0)
- Bot detects the newly filled order
- Increments `position_counter` (tracks consecutive positions)
- Calculates TP/SL targets for the new position
- Stores entry price and position side

---

## POSITION CLOSING CONDITIONS

### Multiple Exit Triggers (Checked in Order)

The bot checks exit conditions in this priority order:

```
1. Manual Shutdown (.close_now file)
2. TP/SL Targets (custom take profit/stop loss)
3. Risk Manager Exit Conditions:
   ├─ 3-Position Rule
   ├─ Stop Loss (percentage-based)
   ├─ Take Profit (percentage-based)
   └─ 75% Range Exit Rule
```

---

## DETAILED EXIT CONDITIONS

### 1. MANUAL SHUTDOWN

**Trigger:** `.close_now` file exists in bot directory

**Action:**
```
1. Cancel all open limit orders
2. Close any open market position
3. Remove .close_now file
4. Terminate bot
```

**Code Location:** `bot.py` - `run()` method (first check)

---

### 2. TP/SL TARGETS (Custom Position Targets)

**Trigger:** Current price hits calculated TP or SL price

#### Take Profit Calculation

**Mode: PERCENTAGE**
```
LONG:  TP_Price = Entry_Price × (1 + TP_Percent/100)
       Trigger: current_price >= TP_Price

SHORT: TP_Price = Entry_Price × (1 - TP_Percent/100)
       Trigger: current_price <= TP_Price
```

**Mode: GRID_RANGE**
```
LONG:  TP_Price = Next grid level ABOVE entry price
       Trigger: current_price >= TP_Price

SHORT: TP_Price = Next grid level BELOW entry price
       Trigger: current_price <= TP_Price
```

#### Stop Loss Calculation

**Always Percentage-Based:**
```
LONG:  SL_Price = Entry_Price × (1 - SL_Percent/100)
       Trigger: current_price <= SL_Price

SHORT: SL_Price = Entry_Price × (1 + SL_Percent/100)
       Trigger: current_price >= SL_Price
```

**Action When Triggered:**
```
1. Log TP/SL trigger event
2. Close position with market order
3. Clear position targets
4. Grid remains active (can open new positions)
```

**Code Location:** `bot.py` - `check_tp_sl_targets()` method

---

### 3. 3-POSITION RULE

**Trigger:** `position_counter >= 3`

**Meaning:** 3 consecutive positions have been opened without a full grid reset

**Action:**
```
1. Cancel all open limit orders
2. Close any open market position
3. Reset position_counter = 0
4. Set is_grid_active = False
5. Generate new grid on next cycle
```

**Code Location:** `risk.py` - `check_exit_conditions()` method

---

### 4. STOP LOSS (Risk Manager)

**Trigger:** Current price moves against position by SL percentage

**Calculation:**
```
LONG:  SL_Price = Entry_Price × (1 - SL_Percent/100)
       Trigger: current_price <= SL_Price

SHORT: SL_Price = Entry_Price × (1 + SL_Percent/100)
       Trigger: current_price >= SL_Price
```

**Example (LONG, Entry=$100, SL=2%):**
```
SL_Price = 100 × (1 - 0.02) = $98
Trigger when price drops to $98 or below
```

**Action:**
```
1. Cancel all open limit orders
2. Close all open positions
3. Reset grid (is_grid_active = False)
4. Generate new grid on next cycle
```

**Code Location:** `risk.py` - `_check_stop_loss()` method

---

### 5. TAKE PROFIT (Risk Manager)

**Trigger:** Current price moves in favor of position by TP percentage

**Calculation:**
```
LONG:  TP_Price = Entry_Price × (1 + TP_Percent/100)
       Trigger: current_price >= TP_Price

SHORT: TP_Price = Entry_Price × (1 - TP_Percent/100)
       Trigger: current_price <= TP_Price
```

**Example (LONG, Entry=$100, TP=5%):**
```
TP_Price = 100 × (1 + 0.05) = $105
Trigger when price rises to $105 or above
```

**Action:**
```
1. Cancel all open limit orders
2. Close all open positions
3. Reset grid (is_grid_active = False)
4. Generate new grid on next cycle
```

**Code Location:** `risk.py` - `_check_take_profit()` method

---

### 6. 75% RANGE EXIT RULE

**Trigger:** Price moves 75% beyond grid boundaries

**Calculation:**
```
Grid_Width = END_PRICE - START_PRICE
Grid_Center = Current_Price (when grid generated)
Grid_Lower = Grid_Center - (Grid_Width / 2)
Grid_Upper = Grid_Center + (Grid_Width / 2)

Exit_Threshold = Grid_Width × 0.75

Lower_Exit_Price = Grid_Lower - Exit_Threshold
Upper_Exit_Price = Grid_Upper + Exit_Threshold

Trigger: current_price <= Lower_Exit_Price OR current_price >= Upper_Exit_Price
```

**Example:**
```
START_PRICE = 60000, END_PRICE = 70000
Grid_Width = 10000
Grid_Center = 65000 (current price when grid generated)
Grid_Lower = 60000, Grid_Upper = 70000

Exit_Threshold = 10000 × 0.75 = 7500

Lower_Exit_Price = 60000 - 7500 = 52500
Upper_Exit_Price = 70000 + 7500 = 77500

Trigger when price < 52500 or price > 77500
```

**Action:**
```
1. Cancel all open limit orders
2. Close all open positions
3. Reset grid (is_grid_active = False)
4. Generate new grid on next cycle
```

**Code Location:** `risk.py` - `_check_75_percent_range_rule()` method

---

## POSITION STATE TRACKING

### Key Variables

```python
self.is_grid_active          # Boolean: Is grid currently active?
self.open_positions          # List: Current open positions
self.position_counter        # Integer: Count of consecutive open positions
self.position_targets        # Dict: TP/SL targets for current position
self._last_position_amt      # Float: Previous position amount (for detection)
```

### Position Detection Logic

```python
# When grid is active, check for new positions
if self.open_positions:
    # New position detected if:
    # 1. Position amount != 0
    # 2. _last_position_amt was 0 (position just opened)
    
    if not hasattr(self, '_last_position_amt') or self._last_position_amt == 0:
        self.position_counter += 1  # Increment counter
        # Calculate TP/SL targets
        entry_price = self.open_positions[0]['entryPrice']
        self.position_targets = self.calculate_tp_sl_targets(entry_price)
    
    self._last_position_amt = float(self.open_positions[0]['positionAmt'])
else:
    # No position
    self._last_position_amt = 0
    self.position_targets = {}
```

---

## COMPLETE WORKFLOW DIAGRAM

```
START BOT
    ↓
┌─────────────────────────────────────┐
│ Check for .close_now file           │
│ (Manual shutdown signal)            │
└─────────────────────────────────────┘
    ↓ (No)
┌─────────────────────────────────────┐
│ Get current market price            │
└─────────────────────────────────────┘
    ↓
    ├─ Is grid active?
    │
    ├─ YES:
    │   ├─ Get position information
    │   ├─ Check TP/SL targets → CLOSE if triggered
    │   ├─ Check Risk Manager conditions:
    │   │   ├─ 3-Position Rule? → RESET GRID
    │   │   ├─ Stop Loss? → RESET GRID
    │   │   ├─ Take Profit? → RESET GRID
    │   │   └─ 75% Range Rule? → RESET GRID
    │   └─ Continue to next cycle
    │
    └─ NO:
        ├─ Generate new grid centered at current price
        ├─ Place limit orders at each grid level
        ├─ Set is_grid_active = True
        └─ Continue to next cycle
```

---

## CONFIGURATION PARAMETERS

### Key .env Variables

```env
# Position Opening
MODE=long                          # long, short, or neutral
START_PRICE=60000                  # Grid lower bound
END_PRICE=70000                    # Grid upper bound
GRID_SIZE=100                      # Number of grid levels
POSITION_SIZE=10.0                 # Size per position
POSITION_SIZE_TYPE=QUOTE           # QUOTE or BASE

# Position Closing - TP/SL
TP_MODE=PERCENTAGE                 # PERCENTAGE or GRID_RANGE
TAKE_PROFIT_PERCENT=5              # TP percentage (if TP_MODE=PERCENTAGE)
STOP_LOSS_PERCENT=2                # SL percentage (always percentage-based)

# Position Closing - Risk Rules
ENABLE_RANGE_EXIT_RULE=True        # Enable 75% range exit
LEVERAGE=20                        # Leverage multiplier

# Trading Mode
DUAL_SIDE_POSITION=False           # Hedge mode or one-way mode
TESTNET=True                       # Testnet or mainnet
```

---

## SUMMARY TABLE

| Condition | Trigger | Action | Grid State |
|-----------|---------|--------|-----------|
| **Position Opens** | Limit order fills | Entry price recorded, TP/SL calculated | Active |
| **TP/SL Hit** | Price reaches target | Close position with market order | Stays Active |
| **3-Position Rule** | 3 consecutive positions | Cancel orders, close position, reset | Inactive |
| **Stop Loss** | Price moves against by SL% | Cancel orders, close position, reset | Inactive |
| **Take Profit** | Price moves in favor by TP% | Cancel orders, close position, reset | Inactive |
| **75% Range Rule** | Price beyond 75% of grid | Cancel orders, close position, reset | Inactive |
| **Manual Shutdown** | .close_now file exists | Cancel orders, close position, exit | Terminated |

---

## KEY INSIGHTS

1. **Positions open automatically** when grid limit orders are filled by market price
2. **Multiple exit conditions** can trigger position closure (TP/SL have priority)
3. **Position counter** tracks consecutive positions to enforce the 3-position rule
4. **Grid resets** when major exit conditions trigger (not when TP/SL hit)
5. **TP/SL targets** are calculated per position and checked every cycle
6. **75% range rule** provides a safety mechanism if price moves too far from grid
7. **Decimal precision** is used for accurate price calculations
