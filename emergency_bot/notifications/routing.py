"""
WebSocket routing configuration for the notifications app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket route for language synchronization
    re_path(r"ws/language/(?P<telegram_id>\w+)/$", consumers.LanguageSyncConsumer.as_asgi()),
    
    # WebSocket route for user notifications
    re_path(r"ws/notifications/(?P<telegram_id>\w+)/$", consumers.NotificationConsumer.as_asgi()),
    
    # WebSocket route for report updates
    re_path(r"ws/reports/(?P<report_id>[\w-]+)/$", consumers.ReportUpdateConsumer.as_asgi()),
] 