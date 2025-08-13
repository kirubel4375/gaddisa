#!/usr/bin/env python
"""
Script to test the Telegram bot token.
"""

import os
import sys
import django
import logging
import asyncio
import requests
import json

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from django.conf import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def test_token():
    """Test if the Telegram bot token is valid."""
    token = settings.TELEGRAM_BOT_TOKEN
    
    print(f"Testing Telegram bot token: {token}")
    
    try:
        # Make a request to the Telegram API to get bot info
        url = f"https://api.telegram.org/bot{token}/getMe"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                bot_username = bot_info.get('username')
                bot_name = bot_info.get('first_name')
                
                print(f"Token is valid! Bot: @{bot_username} ({bot_name})")
                return True
            else:
                print(f"Token is invalid. Response: {data}")
                return False
        else:
            print(f"Failed to validate token. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing token: {e}")
        return False

if __name__ == '__main__':
    if test_token():
        sys.exit(0)
    else:
        sys.exit(1) 