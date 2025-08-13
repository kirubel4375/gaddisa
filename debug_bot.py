import os
import sys
import logging
import asyncio
import traceback
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("debug_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get the bot token from environment variable or file
def get_bot_token():
    # Try environment variable first
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token:
        return token
        
    # Try to read from file
    try:
        with open('bot_token.txt', 'r') as f:
            return f.read().strip()
    except:
        pass
        
    # Ask for token
    token = input("Please enter your Telegram bot token: ")
    
    # Save token for future use
    with open('bot_token.txt', 'w') as f:
        f.write(token)
        
    return token

# Simple test command
async def start(update: Update, context) -> None:
    """Test the start command."""
    try:
        user = update.effective_user
        await update.message.reply_text(f"Hello {user.first_name}! This is a test bot.")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        traceback.print_exc()
        await update.message.reply_text("An error occurred. Check the logs.")

async def test(update: Update, context) -> None:
    """Echo the message text as a test."""
    try:
        await update.message.reply_text(f"You said: {update.message.text}")
    except Exception as e:
        logger.error(f"Error in test command: {e}")
        traceback.print_exc()

def main() -> None:
    """Start the bot."""
    try:
        # Get the bot token
        token = get_bot_token()
        
        # Create the Application
        logger.info("Creating application...")
        application = (
            Application.builder()
            .token(token)
            .connect_timeout(30.0)
            .read_timeout(30.0)
            .write_timeout(30.0)
            .build()
        )
        
        # Test bot connection
        async def test_connection():
            bot = Bot(token=token)
            try:
                me = await bot.get_me()
                logger.info(f"Connected to bot: {me.first_name} (@{me.username})")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to bot: {e}")
                traceback.print_exc()
                return False
        
        # Run the test connection
        if not asyncio.run(test_connection()):
            logger.error("Bot connection test failed. Check your token and internet connection.")
            return
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, test))
        
        # Start the Bot
        logger.info("Starting bot polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting debug bot...")
    main()
    print("Debug bot stopped.") 