import logging
import os
from .config import LOG_LEVEL

def get_logger(name):
    """
    Creates and returns a logger with the specified name.
    
    Args:
        name (str): The name of the logger (usually __name__)
    
    Returns:
        logging.Logger: A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handler
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger
