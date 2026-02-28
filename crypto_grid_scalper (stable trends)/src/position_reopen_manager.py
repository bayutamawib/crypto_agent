# src/position_reopen_manager.py

import logging
from decimal import Decimal
from typing import Dict, List, Optional

class PositionReopenManager:
    """
    Manages reopening of grid positions after they close.
    Maintains a queue of positions to reopen and handles the reopening logic.
    """
    
    def __init__(self, config, exchange):
        """
        Initialize the Position Reopen Manager.
        
        Args:
            config (dict): Bot configuration
            exchange (Exchange): Exchange API handler
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.exchange = exchange
        
        # Queue of positions to reopen: list of dicts with grid_level, side, quantity, position_idx
        self.positions_to_reopen: List[Dict] = []
        
        self.logger.info("PositionReopenManager initialized.")
    
    def add_position_to_reopen(self, grid_level: Decimal, side: str, quantity: float, position_idx: str):
        """
        Add a position to the reopen queue.
        
        Args:
            grid_level (Decimal): The grid level price where position closed
            side (str): 'Buy' or 'Sell'
            quantity (float): Position quantity
            position_idx (str): Position index for Bybit API (e.g., '0' for LONG, '1' for SHORT, '2' for BOTH)
        """
        position_data = {
            'grid_level': float(grid_level),
            'side': side,
            'quantity': quantity,
            'position_idx': position_idx,
        }
        
        self.positions_to_reopen.append(position_data)
        self.logger.info(f"Added position to reopen queue: {position_data}")
        self.logger.debug(f"Reopen queue size: {len(self.positions_to_reopen)}")
    
    def process_reopen_queue(self) -> bool:
        """
        Process the reopen queue and place new limit orders.
        
        Returns:
            bool: True if any positions were reopened, False otherwise
        """
        if not self.config['enablePositionReopen']:
            return False
        
        if not self.positions_to_reopen:
            return False
        
        symbol = self.config['symbol']
        reopened_count = 0
        
        # Process each position in the queue
        for position_data in self.positions_to_reopen[:]:  # Use slice to iterate over copy
            try:
                grid_level = position_data['grid_level']
                side = position_data['side']
                quantity = position_data['quantity']
                position_idx = position_data['position_idx']
                
                self.logger.info(f"Reopening position: {side} {quantity} {symbol} at grid level {grid_level}")
                
                # Place new limit order at the same grid level
                result = self.exchange.create_order(
                    symbol=symbol,
                    order_type='LIMIT',
                    quantity=quantity,
                    side=side,
                    price=f"{grid_level:.8f}",
                    position_side=self._get_position_side_from_idx(position_idx)
                )
                
                if result:
                    self.logger.info(f"Position reopened successfully at grid level {grid_level}")
                    # Remove from queue after successful reopen
                    self.positions_to_reopen.remove(position_data)
                    reopened_count += 1
                else:
                    self.logger.error(f"Failed to reopen position at grid level {grid_level}")
                    # Keep in queue for retry
                    
            except Exception as e:
                self.logger.error(f"Error reopening position: {e}")
                # Keep in queue for retry
        
        if reopened_count > 0:
            self.logger.info(f"Reopened {reopened_count} positions. Queue size: {len(self.positions_to_reopen)}")
        
        return reopened_count > 0
    
    def clear_reopen_queue(self):
        """
        Clear the reopen queue (used when grid resets).
        """
        if self.positions_to_reopen:
            self.logger.info(f"Clearing reopen queue with {len(self.positions_to_reopen)} pending positions")
            self.positions_to_reopen.clear()
    
    def get_queue_size(self) -> int:
        """
        Get the current size of the reopen queue.
        
        Returns:
            int: Number of positions waiting to be reopened
        """
        return len(self.positions_to_reopen)
    
    def _get_position_side_from_idx(self, position_idx: str) -> str:
        """
        Convert position index to position side string for API.
        
        Args:
            position_idx (str): Position index ('0', '1', '2')
        
        Returns:
            str: Position side ('LONG', 'SHORT', 'BOTH')
        """
        idx_map = {
            '0': 'LONG',
            '1': 'SHORT',
            '2': 'BOTH',
        }
        return idx_map.get(position_idx, 'BOTH')
    
    def log_queue_status(self):
        """Log the current status of the reopen queue."""
        if self.positions_to_reopen:
            self.logger.debug(f"Reopen queue status ({len(self.positions_to_reopen)} positions):")
            for i, pos in enumerate(self.positions_to_reopen):
                self.logger.debug(f"  [{i}] {pos['side']} {pos['quantity']} @ {pos['grid_level']}")
        else:
            self.logger.debug("Reopen queue is empty")
