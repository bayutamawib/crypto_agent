# main.py

import time
import logging
from src.bot import Bot
from src.config import load_config

def main():
    """
    Main function to initialize and run the trading bot.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    logger.info("==================================")
    logger.info("Initializing trading bot...")
    
    try:
        config = load_config()
        logger.info("Configuration loaded successfully.")

        bot = Bot(config)
        logger.info("Bot initialized successfully.")
        
        logger.info("Starting bot main loop...")
        while True:
            bot.run()
            # Sleep for a short interval to avoid excessive CPU usage
            logger.debug("Sleeping for 10 seconds...")
            time.sleep(10)

    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Bot has been terminated.")
        logger.info("==================================\n")


if __name__ == "__main__":
    main()
