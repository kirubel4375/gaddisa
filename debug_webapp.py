#!/usr/bin/env python
import os
import sys
import django
import logging
import json

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def main():
    from django.conf import settings
    
    # Print important settings
    print("=== Debug WebApp Settings ===")
    print(f"TELEGRAM_BOT_TOKEN: {settings.TELEGRAM_BOT_TOKEN}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    
    # Check if webapp_url.txt exists
    webapp_url_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp_url.txt")
    print(f"webapp_url.txt exists: {os.path.exists(webapp_url_path)}")
    if os.path.exists(webapp_url_path):
        with open(webapp_url_path, 'r') as f:
            print(f"webapp_url.txt content: {f.read().strip()}")
    
    # Print environment variables
    print(f"WEBAPP_URL env: {os.environ.get('WEBAPP_URL')}")
    
    print("=== End Debug ===")

if __name__ == "__main__":
    main() 