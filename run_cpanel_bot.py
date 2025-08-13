#!/usr/bin/env python
"""
Script to run the Telegram bot on cPanel with language support.
"""

import os
import sys
import django
import logging
import requests
import subprocess

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot_log.txt',  # Log to file on cPanel
    filemode='a'
)
logger = logging.getLogger(__name__)

def main():
    # Read WebApp URL from the file
    webapp_url = "https://gaddisa.hdmsoftwaresolutions.com"
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp_url.txt"), 'r') as f:
            url = f.read().strip()
            if url and (url.startswith("http://") or url.startswith("https://")):
                webapp_url = url
                logger.info(f"Using URL from webapp_url.txt: {webapp_url}")
    except Exception as e:
        logger.warning(f"Could not read webapp_url.txt: {e}")
    
    # Set the WebApp URL in the environment
    os.environ['WEBAPP_URL'] = webapp_url
    
    # Test the URL to make sure it's reachable
    try:
        response = requests.head(webapp_url, timeout=5)
        logger.info(f"WebApp URL test result: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing WebApp URL: {e}")
    
    logger.info(f"Starting Telegram bot with WebApp URL: {webapp_url}")
    
    # Run the bot as a subprocess to avoid event loop issues
    try:
        logger.info("Starting bot with language support...")
        
        # Use popen to start the bot in the background
        bot_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_runner.py")
        
        # Create the bot_runner.py file if it doesn't exist
        if not os.path.exists(bot_script):
            with open(bot_script, 'w') as f:
                f.write("""#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from emergency_bot.telegram_bot.bot import create_application

if __name__ == "__main__":
    app = create_application()
    app.run_polling()
""")
            logger.info(f"Created bot runner script at {bot_script}")
        
        # Make the script executable
        try:
            os.chmod(bot_script, 0o755)
        except Exception as e:
            logger.warning(f"Could not make bot runner script executable: {e}")
        
        # Start the bot process
        process = subprocess.Popen([sys.executable, bot_script], 
                                  stdout=open('bot_output.log', 'a'),
                                  stderr=open('bot_error.log', 'a'))
        
        # Write PID to file for later management
        with open('bot.pid', 'w') as f:
            f.write(str(process.pid))
        
        logger.info(f"Bot started with PID {process.pid}")
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1) 