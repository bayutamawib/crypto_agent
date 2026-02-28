# src/risk.py

import logging
from decimal import Decimal

class RiskManager:
    def __init__(self, config, grid):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.grid = grid
        self.logger.info("RiskManager initialized.")

    def check_exit_conditions(self, current_price, open_positions, position_counter=0, entry_price=None):
        """
        Checks all exit conditions (SL, TP, range exit rule, max positions rule) using Decimal for precision.
        The order of checks is important: SL/TP have priority over the range exit.
        Returns a reason string if an exit is triggered, otherwise None.
        """
        current_price_dec = Decimal(str(current_price))

        # Check max consecutive positions rule first
        if self._check_max_consecutive_positions(position_counter):
            return "Max Consecutive Positions Triggered"

        if self.config['stopLossPercent'] and entry_price and self._check_stop_loss(current_price_dec, entry_price):
            return "Stop Loss Triggered"
        
        if self.config['takeProfitPercent'] and entry_price and self._check_take_profit(current_price_dec, entry_price):
            return "Take Profit Triggered"

        if self.config['enableRangeExitRule']:
            if self._check_range_exit_rule(current_price_dec):
                return "Range Exit Rule Triggered"

        return None

    def _check_max_consecutive_positions(self, position_counter):
        """
        Checks if the maximum consecutive positions limit has been reached.
        
        Args:
            position_counter (int): Current position counter
        
        Returns:
            bool: True if limit reached, False otherwise
        """
        max_positions_str = self.config.get('maxConsecutiveGridPositions', '3')
        
        # Handle "unlimited" string
        if isinstance(max_positions_str, str) and max_positions_str.lower() == "unlimited":
            return False
        
        try:
            max_positions = int(max_positions_str)
            if position_counter >= max_positions:
                self.logger.warning(f"Max Consecutive Positions Rule Triggered! {position_counter} >= {max_positions}")
                return True
        except (ValueError, TypeError):
            self.logger.error(f"Invalid maxConsecutiveGridPositions value: {max_positions_str}")
            return False
        
        return False

    def _check_range_exit_rule(self, current_price_dec):
        """
        Checks if the price has moved beyond the configured threshold percentage of the grid range from the boundaries.
        Default threshold is 100% (full grid width).
        """
        active_grid_lower_boundary = self.grid.grid_center_price - (self.grid.grid_width / Decimal('2'))
        active_grid_upper_boundary = self.grid.grid_center_price + (self.grid.grid_width / Decimal('2'))
        
        # Use configurable threshold percentage
        threshold_percent = Decimal(str(self.config['rangeExitThresholdPercent'])) / Decimal('100')
        exit_threshold_amount = self.grid.grid_width * threshold_percent
        
        upper_exit_price = active_grid_upper_boundary + exit_threshold_amount
        lower_exit_price = active_grid_lower_boundary - exit_threshold_amount
        
        if current_price_dec >= upper_exit_price or current_price_dec <= lower_exit_price:
            self.logger.warning(f"Range Exit Rule Triggered ({self.config['rangeExitThresholdPercent']}%)! Price {current_price_dec} crossed boundaries [{lower_exit_price}, {upper_exit_price}]")
            return True
        return False

    def _check_stop_loss(self, current_price_dec, entry_price):
        """Checks if the stop loss percentage has been hit."""
        entry_price_dec = Decimal(str(entry_price))
        sl_percent = Decimal(str(self.config['stopLossPercent'])) / Decimal('100')
        mode = self.config['mode']

        if mode == 'long':
            # For long: stop loss is entry_price * (1 - sl_percent)
            sl_price = entry_price_dec * (Decimal('1') - sl_percent)
            if current_price_dec <= sl_price:
                self.logger.warning(f"Stop Loss Trigger! Price {current_price_dec} <= {sl_price} ({self.config['stopLossPercent']}% below entry {entry_price_dec})")
                return True
        elif mode == 'short':
            # For short: stop loss is entry_price * (1 + sl_percent)
            sl_price = entry_price_dec * (Decimal('1') + sl_percent)
            if current_price_dec >= sl_price:
                self.logger.warning(f"Stop Loss Trigger! Price {current_price_dec} >= {sl_price} ({self.config['stopLossPercent']}% above entry {entry_price_dec})")
                return True
        return False

    def _check_take_profit(self, current_price_dec, entry_price):
        """Checks if the take profit percentage has been hit."""
        entry_price_dec = Decimal(str(entry_price))
        tp_percent = Decimal(str(self.config['takeProfitPercent'])) / Decimal('100')
        mode = self.config['mode']

        if mode == 'long':
            # For long: take profit is entry_price * (1 + tp_percent)
            tp_price = entry_price_dec * (Decimal('1') + tp_percent)
            if current_price_dec >= tp_price:
                self.logger.info(f"Take Profit Trigger! Price {current_price_dec} >= {tp_price} ({self.config['takeProfitPercent']}% above entry {entry_price_dec})")
                return True
        elif mode == 'short':
            # For short: take profit is entry_price * (1 - tp_percent)
            tp_price = entry_price_dec * (Decimal('1') - tp_percent)
            if current_price_dec <= tp_price:
                self.logger.info(f"Take Profit Trigger! Price {current_price_dec} <= {tp_price} ({self.config['takeProfitPercent']}% below entry {entry_price_dec})")
                return True
        return False
