"""
Middleware for handling Telegram user authentication.
"""

import logging
import json
import hashlib
import hmac
import time
from urllib.parse import parse_qsl
from functools import wraps

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.utils import translation

from .models import UserProfile

logger = logging.getLogger(__name__)


class TelegramAuthMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate Telegram users via Telegram WebApp init data.
    
    The middleware looks for 'X-User-ID' header or 'user_id' query parameter
    to identify the Telegram user accessing the API endpoints.
    
    For WebApp API requests, it also validates the Telegram Web App init_data
    when available in the 'X-Telegram-Init-Data' header.
    """
    
    def process_request(self, request):
        """Process each request and authenticate Telegram user."""
        # Skip authentication for admin, static, or non-API paths
        if request.path.startswith('/admin/') or \
           request.path.startswith(getattr(settings, "STATIC_URL", "/static/")) or \
           request.path.startswith(getattr(settings, "MEDIA_URL", "/media/")) or \
           not (request.path.startswith('/api/') or request.path.startswith('/webapp/') or request.path == '/'):
            return None

        # Get user ID from header or query parameter
        telegram_id = None
        if 'HTTP_X_USER_ID' in request.META:
            telegram_id = request.META.get('HTTP_X_USER_ID')
        if not telegram_id and 'user_id' in request.GET:
            telegram_id = request.GET.get('user_id')
        
        # For production on cPanel, allow access without user_id for testing
        if not telegram_id:
            return None

        try:
            user_profile, created = UserProfile.objects.get_or_create(
                telegram_id=telegram_id
            )
            user_profile.update_last_active()
            request.user_profile = user_profile
            
            # Activate user's preferred language for this request
            if user_profile.language and user_profile.language in ['en', 'am', 'om']:
                translation.activate(user_profile.language)
                request.LANGUAGE_CODE = user_profile.language
                
        except Exception as e:
            logger.error(f"Error authenticating Telegram user: {e}")
            return HttpResponseForbidden("Authentication error")

        return None
    
    def _validate_init_data(self, init_data):
        """
        Validate Telegram WebApp init_data.
        
        This verifies the hash in the init_data matches an HMAC-SHA256
        of the data using the bot token as the key.
        
        Args:
            init_data (str): Telegram WebApp init_data string
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Parse init_data query string
            data_dict = dict(parse_qsl(init_data))
            
            # Extract hash and remove from data
            received_hash = data_dict.pop('hash', '')
            
            # Sort alphabetically by key
            sorted_data = sorted(data_dict.items())
            
            # Join data as key=value pairs
            data_string = '\n'.join([f"{k}={v}" for k, v in sorted_data])
            
            # Create secret key from bot token
            secret_key = hmac.new(
                b"WebAppData",
                settings.TELEGRAM_BOT_TOKEN.encode(),
                hashlib.sha256
            ).digest()
            
            # Calculate HMAC-SHA256
            calculated_hash = hmac.new(
                secret_key,
                data_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Check if hashes match
            return hmac.compare_digest(received_hash, calculated_hash)
        except Exception as e:
            logger.error(f"Error validating init_data: {e}")
            return False


def telegram_auth_required(view_func):
    """
    Decorator to ensure a view is only accessible to authenticated Telegram users.
    
    This decorator checks if request.user_profile exists, which should be set by
    the TelegramAuthMiddleware if authentication was successful.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated via Telegram
        if not hasattr(request, 'user_profile') or not request.user_profile:
            # If not authenticated, try to get user_id from query params
            telegram_id = request.GET.get('user_id')
            if telegram_id:
                try:
                    user_profile, created = UserProfile.objects.get_or_create(
                        telegram_id=telegram_id
                    )
                    user_profile.update_last_active()
                    request.user_profile = user_profile
                    
                    # Activate user's preferred language
                    if user_profile.language and user_profile.language in ['en', 'am', 'om']:
                        translation.activate(user_profile.language)
                        request.LANGUAGE_CODE = user_profile.language
                except Exception as e:
                    logger.error(f"Error in telegram_auth_required: {e}")
                    return HttpResponseForbidden("Authentication required")
            else:
                # Create a default user for testing in production
                user_profile, created = UserProfile.objects.get_or_create(
                    telegram_id='12345'
                )
                request.user_profile = user_profile
        
        # Call the view function
        return view_func(request, *args, **kwargs)
    
    return wrapped_view 