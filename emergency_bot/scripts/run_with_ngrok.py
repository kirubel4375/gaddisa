#!/usr/bin/env python
"""
Script to run the Django server and Telegram bot with ngrok tunneling.
"""

import os
import sys
import time
import subprocess
import requests
import json
import logging
import signal
import atexit
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Global variables
processes = []

def start_django_server():
    """Start the Django development server."""
    logger.info("Starting Django server...")
    django_process = subprocess.Popen(
        ["python", "manage.py", "runserver"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    processes.append(django_process)
    logger.info("Django server started.")
    return django_process

def start_ngrok():
    """Start ngrok tunnel to expose the local server."""
    logger.info("Starting ngrok tunnel...")
    
    # Check if ngrok is installed
    try:
        # Start ngrok process
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append(ngrok_process)
        logger.info("ngrok started.")
        
        # Wait for ngrok to start up
        time.sleep(3)
        
        # Get the ngrok URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = json.loads(response.text)["tunnels"]
            if tunnels:
                ngrok_url = tunnels[0]["public_url"]
                logger.info(f"ngrok tunnel established: {ngrok_url}")
                return ngrok_url
            else:
                logger.error("No ngrok tunnels found.")
                return None
        except Exception as e:
            logger.error(f"Error getting ngrok URL: {e}")
            return None
    except FileNotFoundError:
        logger.error("ngrok not found. Please install ngrok and make sure it's in your PATH.")
        logger.info("You can download ngrok from: https://ngrok.com/download")
        return None

def start_bot(ngrok_url):
    """Start the Telegram bot with the ngrok URL."""
    logger.info(f"Starting Telegram bot with URL: {ngrok_url}")
    
    # Set environment variable for the bot
    env = os.environ.copy()
    env["WEBAPP_URL"] = ngrok_url
    
    # Start the bot process
    bot_process = subprocess.Popen(
        ["python", "emergency_bot/scripts/run_bot.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    processes.append(bot_process)
    logger.info("Telegram bot started.")
    return bot_process

def set_telegram_webhook(ngrok_url):
    """Set the webhook for the Telegram bot"""
    logger.info(f"Setting Telegram webhook for URL: {ngrok_url}")
    
    # Use subprocess to run the update_ngrok_url.py script
    try:
        webhook_process = subprocess.Popen(
            ["python", "update_ngrok_url.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = webhook_process.communicate(timeout=30)
        
        if webhook_process.returncode == 0:
            logger.info("Webhook set successfully!")
            return True
        else:
            logger.error(f"Failed to set webhook: {stderr}")
            return False
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return False

def cleanup():
    """Clean up processes on exit."""
    logger.info("Cleaning up processes...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    logger.info("All processes terminated.")

def main():
    """Main function to run the server and bot."""
    # Register cleanup function
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    # Start Django server
    django_process = start_django_server()
    
    # Wait for Django to start
    time.sleep(3)
    
    # Start ngrok
    ngrok_url = start_ngrok()
    if not ngrok_url:
        logger.error("Failed to start ngrok. Exiting...")
        cleanup()
        sys.exit(1)
    
    # Make sure the URL is using https
    if ngrok_url.startswith("http://"):
        ngrok_url = ngrok_url.replace("http://", "https://")
    
    # Set the webhook
    set_telegram_webhook(ngrok_url)
    
    # Start the bot
    bot_process = start_bot(ngrok_url)
    
    # Monitor processes
    try:
        while True:
            # Check if Django server is still running
            if django_process.poll() is not None:
                logger.error("Django server stopped unexpectedly.")
                break
            
            # Check if bot is still running
            if bot_process.poll() is not None:
                logger.error("Telegram bot stopped unexpectedly.")
                break
            
            # Sleep to avoid high CPU usage
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 