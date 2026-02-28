# src/exchange.py

import logging
import time
from pybit.unified_trading import HTTP

class Exchange:
    def __init__(self, api_key, api_secret, testnet=True):
        self.logger = logging.getLogger(__name__)
        self.testnet = testnet
        
        try:
            # Initialize Bybit client
            self.client = HTTP(
                testnet=testnet,
                api_key=api_key,
                api_secret=api_secret
            )
            self.logger.info("Bybit API client initialized.")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Bybit API client: {e}")
            raise

    def set_position_mode(self, dual_side=False):
        """Sets the position mode (hedge mode or one-way mode)."""
        try:
            response = self.client.switch_position_mode(
                category="linear",
                mode=1 if dual_side else 0  # 1 = hedge mode, 0 = one-way mode
            )
            
            if response['retCode'] == 0:
                mode_name = "Hedge Mode (Dual-Side)" if dual_side else "One-Way Mode"
                self.logger.info(f"Position mode set to {mode_name}.")
                return True
            else:
                self.logger.error(f"Failed to set position mode: {response['retMsg']}")
                return False
        except Exception as e:
            self.logger.error(f"API Error setting position mode: {e}")
            return False

    def get_position_mode(self):
        """Gets the current position mode."""
        try:
            response = self.client.get_position_mode(category="linear")
            
            if response['retCode'] == 0:
                data = response['result']
                dual_side = data.get('isHedgeMode') == 1
                mode_name = "Hedge Mode (Dual-Side)" if dual_side else "One-Way Mode"
                self.logger.info(f"Current position mode: {mode_name}")
                return dual_side
            else:
                self.logger.error(f"Failed to get position mode: {response['retMsg']}")
                return None
        except Exception as e:
            self.logger.error(f"API Error getting position mode: {e}")
            return None

    def set_leverage(self, symbol, leverage):
        """Sets the leverage for a given symbol."""
        try:
            response = self.client.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            
            if response['retCode'] == 0:
                self.logger.info(f"Leverage for {symbol} successfully set to {leverage}x.")
                return True
            else:
                self.logger.error(f"Failed to set leverage for {symbol}: {response['retMsg']}")
                return False
        except Exception as e:
            self.logger.error(f"API Error setting leverage for {symbol}: {e}")
            return False

    def get_market_price(self, symbol):
        """Gets the current market price for a symbol."""
        try:
            response = self.client.get_tickers(category="linear", symbol=symbol)
            
            if response['retCode'] == 0:
                data = response['result']['list'][0]
                mark_price = float(data['markPrice'])
                return mark_price
            else:
                self.logger.warning(f"Could not fetch market price for {symbol}: {response['retMsg']}")
                return None
        except Exception as e:
            self.logger.error(f"API Error fetching market price for {symbol}: {e}")
            return None

    def get_symbol_info(self, symbol):
        """Gets symbol information including quantity precision."""
        try:
            response = self.client.get_instruments_info(category="linear", symbol=symbol)
            
            if response['retCode'] == 0:
                data = response['result']['list'][0]
                return data
            else:
                self.logger.warning(f"Could not fetch symbol info for {symbol}: {response['retMsg']}")
                return None
        except Exception as e:
            self.logger.error(f"API Error fetching symbol info for {symbol}: {e}")
            return None

    def create_order(self, symbol, order_type, quantity, side, price=None, position_side='BOTH'):
        """Creates a futures order."""
        try:
            # Convert quantity to float for calculations
            quantity_float = float(quantity)

            # Get symbol info to determine quantity precision
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info:
                # Get lot size step and minimum quantity
                lot_size_filter = symbol_info.get('lotSizeFilter', {})
                qty_step = float(lot_size_filter.get('qtyStep', 0.01))
                min_qty = float(lot_size_filter.get('minOrderQty', qty_step))
                
                # Round quantity to the nearest valid step
                quantity_float = round(quantity_float / qty_step) * qty_step
                
                # Ensure quantity meets minimum requirement
                if quantity_float < min_qty:
                    self.logger.warning(f"Quantity {quantity_float} is below minimum {min_qty}. Setting to minimum.")
                    quantity_float = min_qty
                
                self.logger.debug(f"Rounded quantity to {quantity_float} (step: {qty_step}, min: {min_qty})")

            # Normalize side to Bybit format (Buy/Sell)
            bybit_side = 'Buy' if side.upper() == 'BUY' else 'Sell' if side.upper() == 'SELL' else side
            
            # Normalize order type to Bybit format (Limit/Market)
            bybit_order_type = 'Limit' if order_type.upper() == 'LIMIT' else 'Market' if order_type.upper() == 'MARKET' else order_type

            params = {
                'category': 'linear',
                'symbol': symbol,
                'side': bybit_side,
                'orderType': bybit_order_type,
                'qty': str(quantity_float),
                'timeInForce': 'GTC',
            }
            
            if bybit_order_type == 'Limit':
                if price is None:
                    self.logger.error("Price is required for LIMIT orders")
                    return None
                params['price'] = str(price)

            self.logger.info(f"Creating order: {params}")
            response = self.client.place_order(**params)
            
            if response['retCode'] == 0:
                self.logger.info(f"Order created: {response['result']}")
                return response['result']
            else:
                self.logger.error(f"Failed to create order for {symbol}: {response['retMsg']}")
                return None
        except Exception as e:
            self.logger.error(f"API Error creating order for {symbol}: {e}")
            return None

    def get_position_information(self, symbol):
        """Gets information about the current position for a symbol."""
        try:
            response = self.client.get_positions(category="linear", symbol=symbol)
            
            if response['retCode'] == 0:
                positions = response['result']['list']
                for position in positions:
                    if position['symbol'] == symbol:
                        # Map Bybit response to consistent structure
                        position_amt = float(position['size'])
                        
                        return {
                            'symbol': position['symbol'],
                            'positionAmt': str(position_amt),
                            'entryPrice': position['avgPrice'],
                        }
                return None
            else:
                self.logger.error(f"Failed to get position info for {symbol}: {response['retMsg']}")
                return None
        except Exception as e:
            self.logger.error(f"API Error fetching position info for {symbol}: {e}")
            return None

    def close_position_market(self, symbol, quantity, side, position_side='BOTH'):
        """Closes a position with a market order."""
        try:
            # Normalize side to Bybit format (Buy/Sell)
            bybit_side = 'Buy' if side.upper() == 'BUY' else 'Sell' if side.upper() == 'SELL' else side
            
            params = {
                'category': 'linear',
                'symbol': symbol,
                'side': bybit_side,
                'orderType': 'Market',
                'qty': str(float(quantity)),
                'reduceOnly': True,
            }
            
            self.logger.info(f"Closing position with market order: {params}")
            response = self.client.place_order(**params)
            
            if response['retCode'] == 0:
                self.logger.info(f"Position closed: {response['result']}")
                return response['result']
            else:
                self.logger.error(f"Failed to close position for {symbol}: {response['retMsg']}")
                return None
        except Exception as e:
            self.logger.error(f"API Error closing position for {symbol}: {e}")
            return None

    def close_all_positions(self, symbol):
        """Closes all open positions for a given symbol."""
        try:
            position = self.get_position_information(symbol)
            if position and float(position['positionAmt']) != 0:
                position_amt = float(position['positionAmt'])
                
                # Determine side to close position
                # Normalize to Bybit format (Buy/Sell)
                side = 'Sell' if position_amt > 0 else 'Buy'
                
                # The quantity to close is the absolute value of the position amount
                quantity = abs(position_amt)

                self.logger.info(f"Closing position for {symbol}. Side: {side}, Quantity: {quantity}")
                
                response = self.client.place_order(
                    category='linear',
                    symbol=symbol,
                    side=side,
                    orderType='Market',
                    qty=str(quantity),
                    reduceOnly=True
                )
                
                if response['retCode'] == 0:
                    self.logger.info(f"Close order executed: {response['result']}")
                    return response['result']
                else:
                    self.logger.error(f"Failed to close position for {symbol}: {response['retMsg']}")
                    return None
            else:
                self.logger.info(f"No open position found for {symbol} to close.")
                return None
        except Exception as e:
            self.logger.error(f"API Error closing positions for {symbol}: {e}")
            return None

    def cancel_all_open_orders(self, symbol):
        """Cancels all open orders for a given symbol."""
        try:
            response = self.client.cancel_all_orders(category="linear", symbol=symbol)
            
            if response['retCode'] == 0:
                self.logger.info(f"All open orders for {symbol} have been cancelled.")
                return True
            else:
                self.logger.error(f"Failed to cancel orders for {symbol}: {response['retMsg']}")
                return False
        except Exception as e:
            self.logger.error(f"API Error cancelling orders for {symbol}: {e}")
            return False
