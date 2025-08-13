#!/usr/bin/env python
import sys
import requests
from urllib.parse import urljoin

# Bot token from settings.py
TELEGRAM_BOT_TOKEN = "7697446317:AAGfXeRSQqbqdmZOg5KqkyzY7ZuSONLPdrU"

def set_webhook():
    """Set the webhook for the Telegram bot using the production domain"""
    webhook_url = "http://gaddisa.hdmsoftwaresolutions.com/telegram/webhook/"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    print(f"Setting Telegram webhook to: {webhook_url}")
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if data.get("ok"):
            print("✅ Webhook set successfully!")
            return True
        else:
            print(f"❌ Failed to set webhook: {data.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def display_instructions(ngrok_url):
    print("\n" + "="*80)
    print(f"Emergency Reporting System is now accessible at: {ngrok_url}")
    print("\nTo test in your browser:")
    print(f"  {ngrok_url}/?user_id=12345")
    print("\nTo use in Telegram:")
    print("  1. Open Telegram and find your bot: @demogaddisa_bot")
    print("  2. Start a chat with the bot using /start")
    print("  3. The bot should display a button to open the Emergency App")
    print("="*80 + "\n")
    
    # Also save the URL to a file for reference
    try:
        with open("ngrok_url.txt", "w") as f:
            f.write(ngrok_url)
        print("URL saved to ngrok_url.txt for reference")
    except:
        pass

def main():
    set_webhook()
    display_instructions("http://gaddisa.hdmsoftwaresolutions.com")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 