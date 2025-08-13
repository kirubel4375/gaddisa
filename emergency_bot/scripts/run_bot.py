#!/usr/bin/env python
"""
Script to run the Telegram bot in development mode.
"""

import os
import sys
import django
import logging
import asyncio

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def main():
    from emergency_bot.telegram_bot.bot import create_application
    
    # Get WebApp URL from environment variable or use default
    webapp_url = os.environ.get('WEBAPP_URL', 'http://localhost:8000')
    
    logger.info(f"Starting Telegram bot with WebApp URL: {webapp_url}")
    
    # Set the WebApp URL in the environment
    os.environ['WEBAPP_URL'] = webapp_url
    
    try:
        # Create the application
        application = create_application()
        
        # Test connection to Telegram API
        logger.info("Testing connection to Telegram API...")
        try:
            me = await application.bot.get_me()
            logger.info(f"Connected to Telegram API. Bot username: @{me.username}")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram API: {e}")
            logger.info("Please check your internet connection and bot token.")
            return
        
        # Start polling
        logger.info("Starting polling...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Keep the script running until interrupted
        try:
            # Wait for a keyboard interrupt
            while True:
                await asyncio.sleep(1)
        finally:
            # Stop the bot when interrupted
            logger.info("Stopping bot...")
            await application.updater.stop_polling()
            await application.stop()
            await application.shutdown()
            logger.info("Bot stopped.")
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1) 