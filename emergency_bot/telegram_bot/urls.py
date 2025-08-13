"""
URL configuration for the telegram_bot app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Webhook endpoint for Telegram
    path('webhook/', views.webhook, name='telegram_webhook'),
    
    # Set webhook URL
    path('set-webhook/', views.set_webhook, name='set_webhook'),
    
    # Test bot endpoint
    path('test-bot/', views.test_bot, name='test_bot'),
] 