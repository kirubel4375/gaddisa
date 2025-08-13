from django.urls import path
from . import views

urlpatterns = [
    # Get user's notifications
    path('', views.get_notifications, name='notification_list'),
    
    # Mark notification as read
    path('<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Update notification settings
    path('settings/update/', views.update_notification_settings, name='update_notification_settings'),
    
    # Send test notification
    path('test/', views.send_test_notification, name='send_test_notification'),
]