import sys
import os
import logging

# Configure logging
logging.basicConfig(
    filename='passenger_error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
    
    # Set WEBAPP_URL environment variable from webapp_url.txt if it exists
    try:
        with open(os.path.join(os.path.dirname(__file__), "webapp_url.txt"), 'r') as f:
            url = f.read().strip()
            if url:
                os.environ['WEBAPP_URL'] = url
                logging.info(f"Set WEBAPP_URL to {url}")
    except Exception as e:
        logging.error(f"Error reading webapp_url.txt: {e}")
    
    # Import the Django WSGI application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
except Exception as e:
    logging.error(f"Error in passenger_wsgi.py: {e}", exc_info=True)
    # Re-raise the exception to see it in the server logs
    raise 