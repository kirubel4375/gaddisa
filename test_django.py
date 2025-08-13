#!/usr/bin/env python
import os
import sys
import django
import requests

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

def main():
    from django.conf import settings
    
    # Get the domain from webapp_url.txt
    domain = "gaddisa.hdmsoftwaresolutions.com"
    try:
        with open("webapp_url.txt", "r") as f:
            url = f.read().strip()
            if url:
                if url.startswith("http://"):
                    domain = url[7:]
                elif url.startswith("https://"):
                    domain = url[8:]
                domain = domain.split('/')[0]
    except Exception as e:
        print(f"Error reading webapp_url.txt: {e}")
    
    print(f"Testing domain: {domain}")
    
    # Test basic connection
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        print(f"Basic connection test: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type')}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Print Django settings
    print("\nDjango Settings:")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'Not set')}")
    print(f"CORS_ALLOWED_ORIGINS: {getattr(settings, 'CORS_ALLOWED_ORIGINS', 'Not set')}")
    
    # Check if templates directory exists
    from django.template.loaders.app_directories import get_app_template_dirs
    template_dirs = list(get_app_template_dirs('templates'))
    print("\nTemplate directories:")
    for directory in template_dirs:
        print(f"  {directory}")
        if os.path.exists(directory):
            print(f"    Contains: {os.listdir(directory)}")
        else:
            print("    Directory does not exist")
    
    # Check if static files are configured correctly
    print("\nStatic files configuration:")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', 'Not set')}")

if __name__ == "__main__":
    main() 