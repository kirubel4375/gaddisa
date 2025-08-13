"""
Views for the notifications app.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification, NotificationChannel

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_notifications(request):
    """
    Get notifications for the current user.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    try:
        # Get unread notifications
        notifications = Notification.objects.filter(
            user=request.user_profile,
            is_read=False
        ).order_by('-created_at')[:10]
        
        # Format notifications
        notification_data = []
        for notification in notifications:
            notification_data.append({
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat(),
                'related_report': str(notification.related_report.id) if notification.related_report else None,
                'related_agency': str(notification.related_agency.id) if notification.related_agency else None,
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notification_data
        })
    
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    try:
        # Get notification and ensure it belongs to the user
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user_profile
        )
        
        # Mark as read
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def update_notification_settings(request):
    """
    Update notification channel settings.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        channel_type = data.get('channel_type')
        is_enabled = data.get('is_enabled')
        
        if not channel_type or is_enabled is None:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)
        
        # Update or create notification channel
        channel, created = NotificationChannel.objects.update_or_create(
            user=request.user_profile,
            channel_type=channel_type,
            defaults={'is_enabled': is_enabled}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Notification settings updated',
            'channel': {
                'type': channel.channel_type,
                'is_enabled': channel.is_enabled
            }
        })
    
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@require_POST
def send_test_notification(request):
    """
    Send a test notification to the user.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    try:
        # Create test notification
        notification = Notification.objects.create(
            user=request.user_profile,
            title="Test Notification",
            message="This is a test notification from the system.",
            notification_type="system",
            priority="medium"
        )
        
        # Send via WebSocket if available
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{request.user_profile.telegram_id}",
            {
                "type": "notification_message",
                "notification_id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "priority": notification.priority,
                "timestamp": notification.created_at.isoformat(),
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Test notification sent',
            'notification_id': str(notification.id)
        })
    
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 