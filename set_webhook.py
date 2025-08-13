#!/usr/bin/env python
import os
import sys
import django
import requests
import logging

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from django.conf import settings

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hardcoded production URL - replace with your actual URL if needed
PRODUCTION_URL = "http://gaddisa.hdmsoftwaresolutions.com"

def set_webhook():
    """Set the webhook URL for the Telegram bot."""
    try:
        # Get the bot token
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Set the webhook URL
        webhook_url = f"{PRODUCTION_URL}/telegram/webhook/"
        
        # Make the request to Telegram API
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            params={'url': webhook_url}
        )
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info(f"Webhook set successfully to {webhook_url}")
                print(f"Webhook set successfully to {webhook_url}")
            else:
                logger.error(f"Failed to set webhook: {result}")
                print(f"Failed to set webhook: {result}")
        else:
            logger.error(f"Failed to set webhook: {response.text}")
            print(f"Failed to set webhook: {response.text}")
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        print(f"Error setting webhook: {e}")

def get_webhook_info():
    """Get information about the current webhook."""
    try:
        # Get the bot token
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Make the request to Telegram API
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        )
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                logger.info(f"Webhook info: {webhook_info}")
                print(f"Webhook info: {webhook_info}")
            else:
                logger.error(f"Failed to get webhook info: {result}")
                print(f"Failed to get webhook info: {result}")
        else:
            logger.error(f"Failed to get webhook info: {response.text}")
            print(f"Failed to get webhook info: {response.text}")
            
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        print(f"Error getting webhook info: {e}")

if __name__ == "__main__":
    # Set the webhook
    set_webhook()
    
    # Get webhook info
    get_webhook_info() 