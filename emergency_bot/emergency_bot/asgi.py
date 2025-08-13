"""
ASGI config for the Emergency Reporting System.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings.dev')
django.setup()

# Import routing after Django setup
from notifications import routing as notifications_routing

# Get the ASGI application
django_asgi_app = get_asgi_application()

# Configure the ASGI application
application = ProtocolTypeRouter({
    # Django's ASGI application to handle HTTP requests
    "http": django_asgi_app,
    
    # WebSocket handler for real-time notifications
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                notifications_routing.websocket_urlpatterns
            )
        )
    ),
}) 