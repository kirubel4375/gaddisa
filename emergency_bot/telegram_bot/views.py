"""
Views for the telegram_bot app.
"""

import json
import logging
import requests
import asyncio
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from telegram import Update
from asgiref.sync import async_to_sync

# Import bot application
from emergency_bot.telegram_bot.bot import create_application

logger = logging.getLogger(__name__)

# Create a single application instance to reuse
_application = None

def get_application():
    """Get or create the application instance."""
    global _application
    try:
        if _application is None:
            logger.info("Creating new application instance")
            _application = create_application()
            # Initialize the application
            _application.initialize()
            logger.info("Application initialized successfully")
        else:
            logger.info("Reusing existing application instance")
        return _application
    except Exception as e:
        logger.error(f"Error getting/creating application: {e}", exc_info=True)
        # Try to create a new instance if the existing one is broken
        try:
            logger.info("Attempting to create a new application instance")
            _application = create_application()
            _application.initialize()
            logger.info("New application instance created successfully")
            return _application
        except Exception as e2:
            logger.error(f"Failed to create new application instance: {e2}", exc_info=True)
            raise e2

@csrf_exempt
def webhook(request):
    """
    Handle incoming webhook requests from Telegram.
    """
    if request.method == 'POST':
        try:
            update_data = json.loads(request.body)
            logger.info(f"Received webhook: {update_data}")

            app = get_application()
            update = Update.de_json(update_data, app.bot)

            async def handle_update():
                if not getattr(app, '_is_initialized', False):
                    await app.initialize()
                    app._is_initialized = True
                await app.process_update(update)

            async_to_sync(handle_update)()
            return HttpResponse('OK')
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return HttpResponse(f'Error: {str(e)}', status=500)

    return HttpResponse('Method not allowed', status=405)


def set_webhook(request):
    """
    Set up the webhook URL for the Telegram bot.
    """
    if request.method == 'GET':
        try:
            bot_token = settings.TELEGRAM_BOT_TOKEN
            webhook_url = f"https://{request.get_host()}/telegram/webhook/"
            
            # Set webhook URL
            response = requests.get(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                params={'url': webhook_url}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Webhook set result: {result}")
                return HttpResponse('Webhook set successfully')
            else:
                logger.error(f"Failed to set webhook: {response.text}")
                return HttpResponse('Failed to set webhook', status=500)
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return HttpResponse(f'Error: {str(e)}', status=500)
    
    return HttpResponse('Method not allowed', status=405)

def test_bot(request):
    """
    Test if the bot token is valid and the webhook URL is accessible.
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Test the bot token by getting bot info
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            
            # Get webhook info
            webhook_response = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
            webhook_info = webhook_response.json() if webhook_response.status_code == 200 else "Error getting webhook info"
            
            # Return bot info and webhook info
            return HttpResponse(
                f"Bot is working! Bot username: @{bot_info['result']['username']}<br><br>"
                f"Bot info: {json.dumps(bot_info, indent=2)}<br><br>"
                f"Webhook info: {json.dumps(webhook_info, indent=2)}"
            )
        else:
            return HttpResponse(f"Bot token is invalid. Response: {response.text}", status=400)
    except Exception as e:
        logger.error(f"Error testing bot: {e}", exc_info=True)
        return HttpResponse(f"Error: {str(e)}", status=500) 