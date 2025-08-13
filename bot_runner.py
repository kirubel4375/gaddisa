#!/usr/bin/env python
"""
Bot runner script for cPanel deployment.
This script runs the bot in a separate process to avoid event loop conflicts.
"""

import os
import sys
import django
import logging
import traceback

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG level for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_output.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Make sure the project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    # Log environment information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Python path: {sys.path}")
    
    # Setup Django environment
    logger.info("Setting up Django environment...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
    django.setup()
    logger.info("Django environment setup complete")
    
    # Read WebApp URL from file
    webapp_url = "https://gaddisa.hdmsoftwaresolutions.com"
    try:
        webapp_url_path = os.path.join(project_root, "webapp_url.txt")
        logger.info(f"Looking for webapp_url.txt at: {webapp_url_path}")
        
        if os.path.exists(webapp_url_path):
            with open(webapp_url_path, 'r') as f:
                url = f.read().strip()
                if url and (url.startswith("http://") or url.startswith("https://")):
                    webapp_url = url
                    logger.info(f"Using URL from webapp_url.txt: {webapp_url}")
        else:
            logger.warning(f"webapp_url.txt not found at {webapp_url_path}")
    except Exception as e:
        logger.warning(f"Could not read webapp_url.txt: {e}")
    
    # Set the WebApp URL in the environment
    os.environ['WEBAPP_URL'] = webapp_url
    logger.info(f"Set WEBAPP_URL environment variable to: {webapp_url}")
    
    # Try importing required modules with detailed error logging
    logger.info("Attempting to import required modules...")
    
    try:
        logger.info("Importing translations module...")
        from emergency_bot.utils.translations import get_text, get_user_language, update_user_language
        logger.info("Successfully imported translations module")
    except ImportError as e:
        logger.error(f"Failed to import translations module: {e}")
        logger.error(traceback.format_exc())
    
    try:
        logger.info("Importing language bridge module...")
        from emergency_bot.telegram_bot.language_bridge import (
            get_user_language_async,
            update_user_language_async,
            language_selection_command,
            language_button_callback
        )
        logger.info("Successfully imported language bridge module")
    except ImportError as e:
        logger.error(f"Failed to import language bridge module: {e}")
        logger.error(traceback.format_exc())
    
    # Import the application creator
    logger.info("Importing bot application creator...")
    try:
        from emergency_bot.telegram_bot.bot import create_application
        logger.info("Successfully imported application creator")
    except ImportError as e:
        logger.error(f"Failed to import application creator: {e}")
        logger.error(traceback.format_exc())
        
        # Fallback to a simple implementation if the import fails
        logger.info("Attempting to create a simple bot application as fallback...")
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, ContextTypes
        from django.conf import settings
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Simple start command"""
            keyboard = [
                [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
                [InlineKeyboardButton("አማርኛ 🇪🇹", callback_data="lang_am")],
                [InlineKeyboardButton("Afaan Oromo 🇪🇹", callback_data="lang_om")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please select your language:", reply_markup=reply_markup)
        
        def create_application():
            """Create a simple application"""
            app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            return app
    
    # Create and run the application
    logger.info("Creating application...")
    app = create_application()
    logger.info("Application created, starting polling...")
    app.run_polling()
    
except Exception as e:
    logger.error(f"Error in bot_runner.py: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)