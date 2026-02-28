# src/market_position_manager.py

import logging
import subprocess
import json
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict

class MarketPositionManager:
    """
    Manages market positions based on Volatility Detector analysis.
    Runs analysis every N minutes and opens/closes positions based on trend and momentum.
    """
    
    def __init__(self, config, exchange):
        """
        Initialize the Market Position Manager.
        
        Args:
            config (dict): Bot configuration
            exchange (Exchange): Exchange API handler
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.exchange = exchange
        
        # State tracking
        self.last_analysis_time = None
        self.last_analysis_result = None
        self.market_position = None  # Track current market position
        self.market_position_entry_price = None
        self.market_position_targets = {}
        self.market_position_reopens = 0  # Track reopens for current signal
        self.last_signal = None  # Track last signal to detect changes
        
        self.logger.info("MarketPositionManager initialized.")
    
    def should_run_analysis(self) -> bool:
        """
        Checks if it's time to run the analysis based on interval.
        
        Returns:
            bool: True if analysis should run, False otherwise
        """
        if self.last_analysis_time is None:
            return True
        
        elapsed = datetime.now() - self.last_analysis_time
        interval = timedelta(minutes=self.config['analysisIntervalMinutes'])
        
        return elapsed >= interval
    
    def run_volatility_detector_analysis(self, symbol: str) -> Optional[Dict]:
        """
        Runs the Volatility Detector analyze_ticker command and parses the output.
        
        Args:
            symbol (str): The cryptocurrency symbol to analyze
        
        Returns:
            dict: Analysis result with trend and momentum, or None if failed
        """
        max_retries = self.config['volatilityDetectorMaxRetries']
        detector_path = self.config['volatilityDetectorPath']
        
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(f"Running Volatility Detector analysis for {symbol} (Attempt {attempt}/{max_retries})...")
                
                # Build command to run analyze_ticker with --json flag
                cmd = [
                    'python', '-m', 'src.bot.analyze_ticker',
                    symbol,
                    self.config['singleTickerInterval'],
                    str(self.config['singleTickerLimit']),
                    '--json'
                ]
                
                # Run the command in the Volatility Detector directory
                result = subprocess.run(
                    cmd,
                    cwd=detector_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    self.logger.error(f"Volatility Detector failed with return code {result.returncode}")
                    self.logger.error(f"STDERR: {result.stderr}")
                    self.logger.error(f"STDOUT: {result.stdout}")
                    if attempt < max_retries:
                        self.logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)
                    continue
                
                # Check if output is empty
                if not result.stdout.strip():
                    self.logger.error("Volatility Detector returned empty output")
                    if attempt < max_retries:
                        self.logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)
                    continue
                
                # Parse JSON output
                analysis_result = json.loads(result.stdout)
                
                # Check if analysis failed (error field present)
                if 'error' in analysis_result:
                    self.logger.error(f"Volatility Detector returned error: {analysis_result.get('error')}")
                    if attempt < max_retries:
                        self.logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)
                    continue
                
                self.logger.info(f"Analysis result: {analysis_result}")
                
                self.last_analysis_time = datetime.now()
                return analysis_result
                
            except subprocess.TimeoutExpired:
                self.logger.error(f"Volatility Detector analysis timed out (Attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    time.sleep(5)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse Volatility Detector output: {e}")
                self.logger.error(f"Raw output: {result.stdout if 'result' in locals() else 'N/A'}")
                if attempt < max_retries:
                    time.sleep(5)
            except Exception as e:
                self.logger.error(f"Error running Volatility Detector: {e}")
                if attempt < max_retries:
                    time.sleep(5)
        
        self.logger.error(f"Volatility Detector analysis failed after {max_retries} retries. Skipping this session.")
        return None
    
    def determine_action(self, analysis_result: Dict) -> Optional[str]:
        """
        Determines what action to take based on analysis result.
        
        Args:
            analysis_result (dict): Result from Volatility Detector analysis
        
        Returns:
            str: Action to take ('OPEN_LONG', 'OPEN_SHORT', 'CLOSE', None)
        """
        trend = analysis_result.get('trend')
        momentum = analysis_result.get('momentum')
        
        self.logger.info(f"Analyzing: Trend={trend}, Momentum={momentum}")
        
        # Create current signal
        current_signal = f"{trend}_{momentum}"
        
        # Check if signal changed
        if self.last_signal and self.last_signal != current_signal:
            self.logger.info(f"Signal changed from {self.last_signal} to {current_signal}. Resetting reopens counter.")
            self.market_position_reopens = 0
        
        self.last_signal = current_signal
        
        # Check if result is same as previous (for position continuation)
        if self.last_analysis_result:
            prev_trend = self.last_analysis_result.get('trend')
            prev_momentum = self.last_analysis_result.get('momentum')
            
            if trend == prev_trend and momentum == prev_momentum:
                self.logger.info("Same analysis result as previous. Continuing current trade.")
                return None
        
        # Store current result for next comparison
        self.last_analysis_result = analysis_result
        
        # Determine action based on conditions
        if trend == "UPTREND" and momentum == "OVERBOUGHT":
            self.logger.info("Condition 1: UPTREND + OVERBOUGHT → Opening LONG position")
            return "OPEN_LONG"
        
        elif trend == "DOWNTREND" and momentum == "OVERSOLD":
            self.logger.info("Condition 2: DOWNTREND + OVERSOLD → Opening SHORT position")
            return "OPEN_SHORT"
        
        elif momentum == "NEUTRAL":
            neutral_action = self.config.get('neutralMomentumAction', 'stop').lower()
            if neutral_action == 'stop':
                self.logger.info("Condition 3: NEUTRAL momentum → Closing market position (NEUTRAL_MOMENTUM_ACTION=stop)")
                return "CLOSE"
            else:
                self.logger.info("Condition 3: NEUTRAL momentum → Continuing current trade (NEUTRAL_MOMENTUM_ACTION=continue)")
                return None
        
        else:
            self.logger.info(f"No matching condition for Trend={trend}, Momentum={momentum}")
            return None
    
    def open_market_position(self, side: str, current_price: Decimal) -> bool:
        """
        Opens a market position (LONG or SHORT).
        
        Args:
            side (str): 'BUY' for LONG, 'SELL' for SHORT
            current_price (Decimal): Current market price
        
        Returns:
            bool: True if position opened successfully, False otherwise
        """
        try:
            symbol = self.config['symbol']
            leverage = self.config['leverage']
            position_size = self.config['positionSize']
            position_size_type = self.config['positionSizeType']
            
            # Calculate quantity
            if position_size_type == 'QUOTE':
                quantity = position_size / float(current_price)
            else:  # BASE
                quantity = position_size
            
            self.logger.info(f"Opening {side} market position for {symbol}")
            self.logger.info(f"Quantity: {quantity}, Price: {current_price}, Leverage: {leverage}x")
            
            # Create market order
            result = self.exchange.create_order(
                symbol=symbol,
                order_type='MARKET',
                quantity=quantity,
                side=side,
                position_side='LONG' if side == 'BUY' else 'SHORT'
            )
            
            if result:
                self.market_position = side
                self.market_position_entry_price = float(current_price)
                
                # Calculate TP/SL targets
                self.market_position_targets = self._calculate_market_position_targets(
                    float(current_price),
                    side
                )
                
                self.logger.info(f"Market position opened successfully. Targets: {self.market_position_targets}")
                return True
            else:
                self.logger.error("Failed to open market position")
                return False
                
        except Exception as e:
            self.logger.error(f"Error opening market position: {e}")
            return False
    
    def close_market_position(self, reopen_on_tp_sl: bool = False) -> bool:
        """
        Closes the current market position.
        
        Args:
            reopen_on_tp_sl (bool): If True, will reopen position if TP/SL was hit and trend is still valid
        
        Returns:
            bool: True if position closed successfully, False otherwise
        """
        try:
            if not self.market_position:
                self.logger.info("No market position to close")
                return True
            
            symbol = self.config['symbol']
            
            # Get current position info
            position_info = self.exchange.get_position_information(symbol)
            if not position_info or float(position_info.get('positionAmt', 0)) == 0:
                self.logger.info("No open market position found")
                self.market_position = None
                self.market_position_targets = {}
                return True
            
            position_amt = float(position_info['positionAmt'])
            quantity = abs(position_amt)
            close_side = 'SELL' if position_amt > 0 else 'BUY'
            
            self.logger.info(f"Closing market position: {close_side} {quantity} {symbol}")
            
            result = self.exchange.close_position_market(
                symbol=symbol,
                quantity=quantity,
                side=close_side,
                position_side='LONG' if position_amt > 0 else 'SHORT'
            )
            
            if result:
                # Store position info for potential reopening
                closed_side = 'BUY' if position_amt > 0 else 'SELL'  # Opposite of close side
                closed_entry_price = float(position_info.get('entryPrice', 0))
                
                self.market_position = None
                self.market_position_entry_price = None
                self.market_position_targets = {}
                
                self.logger.info("Market position closed successfully")
                
                # If TP/SL was hit and we should reopen, return the side for reopening
                if reopen_on_tp_sl:
                    return True, closed_side
                
                return True
            else:
                self.logger.error("Failed to close market position")
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing market position: {e}")
            return False
    
    def _calculate_market_position_targets(self, entry_price: float, side: str) -> Dict:
        """
        Calculates TP/SL targets for market position.
        
        Args:
            entry_price (float): Entry price of the position
            side (str): 'BUY' for LONG, 'SELL' for SHORT
        
        Returns:
            dict: Dictionary with TP and SL prices
        """
        targets = {
            'entry_price': entry_price,
            'side': side,
        }
        
        # Calculate stop loss (always percentage-based)
        if self.config['stopLossPercent']:
            sl_percent = float(self.config['stopLossPercent']) / 100
            if side == 'BUY':  # LONG
                targets['sl_price'] = entry_price * (1 - sl_percent)
            else:  # SHORT
                targets['sl_price'] = entry_price * (1 + sl_percent)
        
        # Calculate take profit
        if self.config['takeProfitPercent']:
            tp_percent = float(self.config['takeProfitPercent']) / 100
            if side == 'BUY':  # LONG
                targets['tp_price'] = entry_price * (1 + tp_percent)
            else:  # SHORT
                targets['tp_price'] = entry_price * (1 - tp_percent)
        
        return targets
    
    def check_market_position_tp_sl(self, current_price: Decimal) -> Optional[str]:
        """
        Checks if market position TP/SL targets are hit.
        
        Args:
            current_price (Decimal): Current market price
        
        Returns:
            str: 'TAKE_PROFIT', 'STOP_LOSS', or None
        """
        if not self.market_position or not self.market_position_targets:
            return None
        
        current_price_float = float(current_price)
        targets = self.market_position_targets
        side = targets.get('side')
        
        # Check take profit
        if 'tp_price' in targets:
            tp_price = targets['tp_price']
            if side == 'BUY' and current_price_float >= tp_price:
                self.logger.warning(f"Market position TAKE PROFIT triggered! Price {current_price_float} >= TP {tp_price}")
                return 'TAKE_PROFIT'
            elif side == 'SELL' and current_price_float <= tp_price:
                self.logger.warning(f"Market position TAKE PROFIT triggered! Price {current_price_float} <= TP {tp_price}")
                return 'TAKE_PROFIT'
        
        # Check stop loss
        if 'sl_price' in targets:
            sl_price = targets['sl_price']
            if side == 'BUY' and current_price_float <= sl_price:
                self.logger.warning(f"Market position STOP LOSS triggered! Price {current_price_float} <= SL {sl_price}")
                return 'STOP_LOSS'
            elif side == 'SELL' and current_price_float >= sl_price:
                self.logger.warning(f"Market position STOP LOSS triggered! Price {current_price_float} >= SL {sl_price}")
                return 'STOP_LOSS'
        
        return None
    
    def _can_reopen_market_position(self) -> bool:
        """
        Checks if market position can be reopened based on max reopens limit.
        
        Returns:
            bool: True if can reopen, False otherwise
        """
        max_reopens_str = self.config.get('maxMarketPositionReopens', 'unlimited')
        
        # Handle "unlimited" string
        if isinstance(max_reopens_str, str) and max_reopens_str.lower() == "unlimited":
            return True
        
        try:
            max_reopens = int(max_reopens_str)
            if self.market_position_reopens >= max_reopens:
                self.logger.warning(f"Max Market Position Reopens Reached! {self.market_position_reopens} >= {max_reopens}")
                return False
        except (ValueError, TypeError):
            self.logger.error(f"Invalid maxMarketPositionReopens value: {max_reopens_str}")
            return True
        
        return True
    
    def process_analysis(self, current_price: Decimal) -> bool:
        """
        Main method to run analysis and process actions.
        
        Args:
            current_price (Decimal): Current market price
        
        Returns:
            bool: True if analysis ran, False otherwise
        """
        if not self.config['enableMarketPositionLogic']:
            return False
        
        if not self.should_run_analysis():
            return False
        
        symbol = self.config['symbol']
        
        # Run analysis
        analysis_result = self.run_volatility_detector_analysis(symbol)
        if not analysis_result:
            return False
        
        # Determine action
        action = self.determine_action(analysis_result)
        if not action:
            return True
        
        # Execute action
        if action == "OPEN_LONG":
            self.close_market_position()  # Close any existing position first
            self.market_position_reopens = 0  # Reset reopens counter
            self.open_market_position('BUY', current_price)
        
        elif action == "OPEN_SHORT":
            self.close_market_position()  # Close any existing position first
            self.market_position_reopens = 0  # Reset reopens counter
            self.open_market_position('SELL', current_price)
        
        elif action == "CLOSE":
            self.close_market_position()
            self.market_position_reopens = 0  # Reset reopens counter
        
        return True
    
    def handle_market_position_tp_sl(self, tp_sl_trigger: str, current_price: Decimal) -> bool:
        """
        Handles TP/SL trigger for market positions - closes and potentially reopens.
        
        Args:
            tp_sl_trigger (str): 'TAKE_PROFIT' or 'STOP_LOSS'
            current_price (Decimal): Current market price
        
        Returns:
            bool: True if position was reopened, False otherwise
        """
        if not self.market_position:
            return False
        
        # Check if we can reopen
        if not self._can_reopen_market_position():
            self.logger.warning(f"Cannot reopen market position - max reopens reached")
            self.close_market_position()
            return False
        
        # Check if trend is still valid (not NEUTRAL)
        if self.last_analysis_result:
            momentum = self.last_analysis_result.get('momentum')
            if momentum == "NEUTRAL":
                self.logger.info(f"Momentum is NEUTRAL - not reopening market position")
                self.close_market_position()
                return False
        
        # Get current position side
        symbol = self.config['symbol']
        position_info = self.exchange.get_position_information(symbol)
        if not position_info:
            return False
        
        position_amt = float(position_info.get('positionAmt', 0))
        if position_amt == 0:
            return False
        
        # Determine reopen side (same as closed position)
        reopen_side = 'BUY' if position_amt > 0 else 'SELL'
        
        self.logger.info(f"{tp_sl_trigger} triggered - closing and reopening market position")
        
        # Close current position
        self.close_market_position()
        
        # Reopen immediately at current price
        self.market_position_reopens += 1
        self.logger.info(f"Market position reopen #{self.market_position_reopens}")
        
        self.open_market_position(reopen_side, current_price)
        return True
