# src/bot.py

import logging
import os
import sys
from src.exchange import Exchange
from src.grid import Grid
from src.risk import RiskManager
from src.market_position_manager import MarketPositionManager
from src.position_reopen_manager import PositionReopenManager

from decimal import Decimal

class Bot:
    def __init__(self, config):
        """
        Initializes the Bot with configuration.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize exchange connection
        self.exchange = Exchange(
            api_key=config['bybitApiKey'],
            api_secret=config['bybitApiSecret'],
            testnet=config['testnet']
        )
        
        # Set position mode if dual-side is enabled
        if config['dualSidePosition']:
            self.logger.info("Setting position mode to Hedge Mode (Dual-Side)...")
            self.exchange.set_position_mode(dual_side=True)
        else:
            self.logger.info("Using One-Way Mode...")
            self.exchange.set_position_mode(dual_side=False)
        
        # Set leverage for the symbol
        self.logger.info(f"Setting leverage to {config['leverage']}x for {config['symbol']}...")
        self.exchange.set_leverage(config['symbol'], config['leverage'])
        
        # Initialize grid
        self.grid = Grid(config)
        
        # Initialize risk manager
        self.risk_manager = RiskManager(config, self.grid)
        
        # Initialize market position manager
        self.market_position_manager = MarketPositionManager(config, self.exchange)
        
        # Initialize position reopen manager
        self.position_reopen_manager = PositionReopenManager(config, self.exchange)
        
        # State tracking
        self.is_grid_active = False
        self.open_positions = []
        self.position_counter = 0  # Track consecutive open positions
        self.position_targets = {}  # Track TP/SL targets for each position
        self._last_position_amt = 0  # Track previous position amount for closure detection
        self._last_entry_price = None  # Track previous entry price
        self._last_position_side = None  # Track previous position side
        
        self.logger.info("Bot initialized successfully.")

    def run(self):
        """
        The main operational loop of the bot.
        """
        # Check for manual shutdown signal
        if os.path.exists(".close_now"):
            self.logger.warning("MANUAL SHUTDOWN DETECTED: '.close_now' file found.")
            
            # 1. Cancel all open limit orders
            self.logger.info("Cancelling all open orders...")
            self.exchange.cancel_all_open_orders(self.config['symbol'])
            
            # 2. Close any open market position
            position_info = self.exchange.get_position_information(self.config['symbol'])
            self.open_positions = [position_info] if position_info and float(position_info.get('positionAmt', 0)) != 0 else []
            if self.open_positions:
                self.logger.info("Closing open market position...")
                self.exchange.close_all_positions(self.config['symbol'])

            # 3. Remove the signal file
            os.remove(".close_now")
            self.logger.info("Signal file '.close_now' removed.")
            
            # 4. Terminate the bot
            self.logger.info("Bot is terminating.")
            sys.exit(0)

        self.logger.debug("Bot is running...")
        
        price_str = self.exchange.get_market_price(self.config['symbol'])
        if not price_str:
            self.logger.error("Could not retrieve market price. Skipping run.")
            return
        current_price = Decimal(str(price_str))
        self.logger.info(f"Current market price for {self.config['symbol']}: {current_price}")

        # Check market position TP/SL (if market position exists)
        if self.market_position_manager.market_position:
            tp_sl_trigger = self.market_position_manager.check_market_position_tp_sl(current_price)
            if tp_sl_trigger:
                self.logger.warning(f"Market position {tp_sl_trigger} triggered.")
                # Handle TP/SL with potential reopening
                self.market_position_manager.handle_market_position_tp_sl(tp_sl_trigger, current_price)

        # Process position reopen queue (place pending limit orders)
        self.position_reopen_manager.process_reopen_queue()

        if self.is_grid_active:
            self.logger.debug("Grid is active. Checking positions and exit conditions.")
            position_info = self.exchange.get_position_information(self.config['symbol'])
            
            # Simplified position tracking
            self.open_positions = [position_info] if position_info and float(position_info.get('positionAmt', 0)) != 0 else []
            
            if self.open_positions:
                self.logger.info(f"Open position found: {self.open_positions[0]['positionAmt']} {self.config['symbol']}.")
                # Increment position counter when a new position is detected
                if not hasattr(self, '_last_position_amt') or self._last_position_amt == 0:
                    self.position_counter += 1
                    self.logger.info(f"Position counter: {self.position_counter}")
                    # Calculate TP/SL targets for the newly opened position
                    entry_price = float(self.open_positions[0]['entryPrice'])
                    position_side = 'LONG' if float(self.open_positions[0]['positionAmt']) > 0 else 'SHORT' if self.config['dualSidePosition'] else 'BOTH'
                    self.position_targets = self.calculate_tp_sl_targets(entry_price, position_side)
                    self._last_entry_price = entry_price
                    self._last_position_side = position_side
                self._last_position_amt = float(self.open_positions[0]['positionAmt'])
            else:
                self.logger.info("No open market position.")
                
                # Detect position closure (position was open, now closed)
                if self._last_position_amt != 0 and self.config['enablePositionReopen']:
                    self.logger.info("Position closure detected! Adding to reopen queue.")
                    
                    # Determine the side for reopening (opposite of what closed)
                    if self._last_position_amt > 0:  # Was LONG, reopen as SHORT
                        reopen_side = 'SELL'
                        position_idx = '1'  # SHORT
                    else:  # Was SHORT, reopen as LONG
                        reopen_side = 'BUY'
                        position_idx = '0'  # LONG
                    
                    # Add to reopen queue
                    self.position_reopen_manager.add_position_to_reopen(
                        grid_level=Decimal(str(self._last_entry_price)),
                        side=reopen_side,
                        quantity=abs(self._last_position_amt),
                        position_idx=position_idx
                    )
                
                self._last_position_amt = 0
                self._last_entry_price = None
                self._last_position_side = None
                self.position_targets = {}

            # Get entry price from position info
            entry_price = float(self.open_positions[0]['entryPrice']) if self.open_positions else None
            
            # Check custom TP/SL targets
            tp_sl_trigger = self.check_tp_sl_targets(current_price)
            if tp_sl_trigger:
                self.logger.warning(f"TP/SL TRIGGER: {tp_sl_trigger}. Closing position.")
                if self.open_positions:
                    position_amt = float(self.open_positions[0]['positionAmt'])
                    quantity = abs(position_amt)
                    side = 'SELL' if position_amt > 0 else 'BUY'
                    position_side = 'LONG' if position_amt > 0 else 'SHORT' if self.config['dualSidePosition'] else 'BOTH'
                    self.exchange.close_position_market(self.config['symbol'], quantity, side, position_side)
                self.position_targets = {}
            
            # Check exit conditions (range exit, 3-position rule)
            exit_reason = self.risk_manager.check_exit_conditions(current_price, self.open_positions, self.position_counter, entry_price)
            if exit_reason:
                self.logger.warning(f"EXIT TRIGGER: {exit_reason}. Resetting grid.")
                
                # 1. Cancel all open limit orders from the old grid
                self.logger.info("Cancelling all open orders...")
                self.exchange.cancel_all_open_orders(self.config['symbol'])
                
                # 2. Close any open market position
                if self.open_positions:
                    self.logger.info("Closing open market position...")
                    self.exchange.close_all_positions(self.config['symbol'])
                
                # 3. Clear reopen queue when grid resets
                self.position_reopen_manager.clear_reopen_queue()
                
                # 4. Reset position counter and mark grid as inactive
                self.position_counter = 0
                self._last_position_amt = 0
                self._last_entry_price = None
                self._last_position_side = None
                self.is_grid_active = False
                self.position_targets = {}
                self.logger.info("Grid has been successfully reset.")
        
        if not self.is_grid_active:
            # Check if grid should be activated based on neutral-only setting
            should_activate_grid = True
            
            if self.config['gridBotNeutralOnly']:
                # Only activate grid if momentum is NEUTRAL
                if self.market_position_manager.last_analysis_result:
                    momentum = self.market_position_manager.last_analysis_result.get('momentum')
                    if momentum != 'NEUTRAL':
                        should_activate_grid = False
                        self.logger.info(f"Grid bot is set to NEUTRAL_ONLY mode. Momentum is {momentum}, not activating grid.")
            
            if should_activate_grid:
                self.logger.info(f"No active grid. Generating a new one centered at {current_price}.")
                self.grid.generate(current_price)
                self.place_grid_orders(current_price)
                self.is_grid_active = True
        
        # Check if grid should be deactivated based on neutral-only setting
        if self.is_grid_active and self.config['gridBotNeutralOnly']:
            if self.market_position_manager.last_analysis_result:
                momentum = self.market_position_manager.last_analysis_result.get('momentum')
                if momentum != 'NEUTRAL':
                    self.logger.warning(f"Grid bot is set to NEUTRAL_ONLY mode. Momentum is {momentum}, deactivating grid.")
                    # Cancel all open orders and close positions
                    self.exchange.cancel_all_open_orders(self.config['symbol'])
                    if self.open_positions:
                        self.exchange.close_all_positions(self.config['symbol'])
                    self.position_reopen_manager.clear_reopen_queue()
                    self.position_counter = 0
                    self._last_position_amt = 0
                    self._last_entry_price = None
                    self._last_position_side = None
                    self.is_grid_active = False
                    self.position_targets = {}
        
        # Process market position analysis (runs every N minutes)
        self.market_position_manager.process_analysis(current_price)

    def place_grid_orders(self, current_price):
        """Places the initial grid of limit orders."""
        self.logger.info("Placing new grid orders...")
        
        for level_price in self.grid.grid_levels:
            position_side = 'BOTH'  # Default for one-way mode
            
            if self.config['dualSidePosition']:
                # Dual-side (hedge) mode
                if self.config['mode'] == 'long':
                    if level_price < current_price:
                        side = 'BUY'
                        position_side = 'LONG'
                    else:
                        continue
                elif self.config['mode'] == 'short':
                    if level_price > current_price:
                        side = 'SELL'
                        position_side = 'SHORT'
                    else:
                        continue
                elif self.config['mode'] == 'neutral':
                    # Neutral mode: place both BUY and SELL orders
                    if level_price < current_price:
                        side = 'BUY'
                        position_side = 'LONG'
                    elif level_price > current_price:
                        side = 'SELL'
                        position_side = 'SHORT'
                    else:
                        continue
            else:
                # One-way mode
                if self.config['mode'] == 'long':
                    if level_price < current_price:
                        side = 'BUY'
                    else:
                        continue
                elif self.config['mode'] == 'short':
                    if level_price > current_price:
                        side = 'SELL'
                    else:
                        continue
                elif self.config['mode'] == 'neutral':
                    # Neutral mode in one-way: place both BUY and SELL orders
                    if level_price < current_price:
                        side = 'BUY'
                    elif level_price > current_price:
                        side = 'SELL'
                    else:
                        continue

            quantity = self._calculate_quantity(level_price)
            if quantity <= 0:
                continue
            
            # Format price for the API
            price_str = f"{level_price:.8f}"

            self.exchange.create_order(
                symbol=self.config['symbol'],
                order_type='LIMIT',
                quantity=round(quantity, 5),
                side=side,
                price=price_str,
                position_side=position_side
            )
    def calculate_tp_sl_targets(self, entry_price, position_side='BOTH'):
        """Calculates take profit and stop loss target prices."""
        entry_price_float = float(entry_price)
        
        targets = {
            'entry_price': entry_price_float,
            'position_side': position_side,
        }
        
        # Calculate stop loss (always percentage-based)
        if self.config['stopLossPercent']:
            if self.config['mode'] == 'long':
                sl_percent = float(self.config['stopLossPercent']) / 100
                targets['sl_price'] = entry_price_float * (1 - sl_percent)
            elif self.config['mode'] == 'short':
                sl_percent = float(self.config['stopLossPercent']) / 100
                targets['sl_price'] = entry_price_float * (1 + sl_percent)
        
        # Calculate take profit based on mode
        if self.config['tpMode'] == 'PERCENTAGE':
            if self.config['takeProfitPercent']:
                if self.config['mode'] == 'long':
                    tp_percent = float(self.config['takeProfitPercent']) / 100
                    targets['tp_price'] = entry_price_float * (1 + tp_percent)
                elif self.config['mode'] == 'short':
                    tp_percent = float(self.config['takeProfitPercent']) / 100
                    targets['tp_price'] = entry_price_float * (1 - tp_percent)
        
        elif self.config['tpMode'] == 'GRID_RANGE':
            # Find the next grid level as TP target
            tp_price = self._find_next_grid_level(entry_price_float)
            if tp_price:
                targets['tp_price'] = tp_price
        
        self.logger.info(f"TP/SL targets calculated: {targets}")
        return targets

    def _find_next_grid_level(self, entry_price):
        """Finds the next grid level above (for LONG) or below (for SHORT) the entry price."""
        if not self.grid.grid_levels:
            self.logger.warning("Grid levels not available")
            return None
        
        entry_price_float = float(entry_price)
        grid_levels = [float(level) for level in self.grid.grid_levels]
        grid_levels.sort()
        
        if self.config['mode'] == 'long':
            # Find the next level above entry price
            for level in grid_levels:
                if level > entry_price_float:
                    self.logger.info(f"Next grid level for LONG: {level}")
                    return level
        elif self.config['mode'] == 'short':
            # Find the next level below entry price
            for level in reversed(grid_levels):
                if level < entry_price_float:
                    self.logger.info(f"Next grid level for SHORT: {level}")
                    return level
        
        return None

    def check_tp_sl_targets(self, current_price):
        """Checks if current price hits any TP/SL targets and closes position if triggered."""
        current_price_float = float(current_price)
        
        if not self.position_targets:
            return None
        
        targets = self.position_targets
        entry_price = targets['entry_price']
        
        # Check take profit
        if 'tp_price' in targets:
            tp_price = targets['tp_price']
            if self.config['mode'] == 'long' and current_price_float >= tp_price:
                self.logger.warning(f"TAKE PROFIT TRIGGERED! Price {current_price_float} >= TP {tp_price}")
                return 'TAKE_PROFIT'
            elif self.config['mode'] == 'short' and current_price_float <= tp_price:
                self.logger.warning(f"TAKE PROFIT TRIGGERED! Price {current_price_float} <= TP {tp_price}")
                return 'TAKE_PROFIT'
        
        # Check stop loss
        if 'sl_price' in targets:
            sl_price = targets['sl_price']
            if self.config['mode'] == 'long' and current_price_float <= sl_price:
                self.logger.warning(f"STOP LOSS TRIGGERED! Price {current_price_float} <= SL {sl_price}")
                return 'STOP_LOSS'
            elif self.config['mode'] == 'short' and current_price_float >= sl_price:
                self.logger.warning(f"STOP LOSS TRIGGERED! Price {current_price_float} >= SL {sl_price}")
                return 'STOP_LOSS'
        
        return None

    
    def _calculate_quantity(self, price):
        """Calculates the order quantity based on position size and type."""
        size = Decimal(str(self.config['positionSize']))
        if self.config['positionSizeType'] == 'BASE':
            return size
        elif self.config['positionSizeType'] == 'QUOTE':
            if price > 0:
                return size / price
            else:
                self.logger.error("Price is zero, cannot calculate quantity for QUOTE size type.")
                return 0
        else:
            self.logger.error(f"Invalid positionSizeType: {self.config['positionSizeType']}")
            return 0
