"""
URL configuration for the accounts app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Verify Telegram user
    path('verify/', views.verify_user, name='verify_user'),
    
    # Get current user profile
    path('me/', views.current_user, name='current_user'),
    
    # Update user preferences
    path('preferences/', views.update_preferences, name='update_preferences'),
    
    # Grant or revoke data consent
    path('consent/', views.update_consent, name='update_consent'),
] 