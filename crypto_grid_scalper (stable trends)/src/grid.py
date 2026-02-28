# src/grid.py

import logging
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 10 

class Grid:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.grid_levels = []
        self.grid_width = Decimal('0')
        self.grid_center_price = Decimal('0')
        self.logger.info("Grid initialized.")

    def generate(self, center_price):
        """
        Generates the grid levels based on the center price.
        gridSize represents the number of divisions of the price range.
        interval = grid_width / gridSize
        """
        center_price_dec = Decimal(str(center_price))
        start_price_dec = Decimal(str(self.config['startPrice']))
        end_price_dec = Decimal(str(self.config['endPrice']))
        grid_divisions = Decimal(str(self.config['gridSize']))

        self.grid_center_price = center_price_dec
        self.grid_width = end_price_dec - start_price_dec
        
        # Calculate interval between grid levels
        interval = self.grid_width / grid_divisions
        
        new_start_price = self.grid_center_price - (self.grid_width / Decimal('2'))
        new_end_price = self.grid_center_price + (self.grid_width / Decimal('2'))
        
        # Clear existing grid levels
        self.grid_levels = []

        current_price = new_start_price
        while current_price <= new_end_price:
            self.grid_levels.append(current_price)
            current_price += interval
            
        self.logger.info(f"Generated {len(self.grid_levels)} grid levels centered at {self.grid_center_price}.")
        self.logger.debug(f"Grid levels: {self.grid_levels}")
        
        return self.grid_levels
