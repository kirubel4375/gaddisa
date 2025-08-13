from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings

# Create your views here.

@csrf_exempt
def webhook(request):
    """Handle incoming webhook requests from Telegram"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process the incoming message
            # Add your bot logic here
            return HttpResponse('OK')
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON', status=400)
    return HttpResponse('Method not allowed', status=405)

def set_webhook(request):
    """Set up the webhook URL for the Telegram bot"""
    if request.method == 'GET':
        try:
            # Replace with your actual bot token
            bot_token = settings.TELEGRAM_BOT_TOKEN
            webhook_url = f"https://{request.get_host()}/webhook/"
            
            # Set webhook URL
            response = requests.get(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                params={'url': webhook_url}
            )
            
            if response.status_code == 200:
                return HttpResponse('Webhook set successfully')
            else:
                return HttpResponse('Failed to set webhook', status=500)
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    return HttpResponse('Method not allowed', status=405)
