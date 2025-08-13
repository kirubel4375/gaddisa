"""
WebSocket consumers for real-time notifications
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import UserProfile
from reports.models import IncidentReport

logger = logging.getLogger(__name__)


class LanguageSyncConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for language synchronization between Telegram bot and mini app.
    
    URL path: /ws/language/<telegram_id>/
    """
    
    async def connect(self):
        self.telegram_id = self.scope["url_route"]["kwargs"]["telegram_id"]
        self.room_group_name = f"language_sync_{self.telegram_id}"
        
        # Check if the user exists
        user_exists = await self.user_exists(self.telegram_id)
        if not user_exists:
            logger.warning(f"Language sync connection attempt for non-existent user: {self.telegram_id}")
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Send current language preference
        await self.send_current_language()
        
        logger.info(f"Language sync WebSocket connected for user {self.telegram_id}")
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Language sync WebSocket disconnected for user {self.telegram_id} with code {close_code}")
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket for language sync requests
        """
        try:
            data_json = json.loads(text_data)
            action = data_json.get("action")
            
            if action == "get_language":
                await self.send_current_language()
            elif action == "update_language":
                language_code = data_json.get("language_code")
                if language_code:
                    success = await self.update_user_language(language_code)
                    await self.send(text_data=json.dumps({
                        "type": "language_update_response",
                        "success": success,
                        "language": language_code if success else None
                    }))
        
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from language sync WebSocket")
        except Exception as e:
            logger.error(f"Error in language sync WebSocket receive: {e}")
    
    async def language_changed(self, event):
        """
        Handle language change notification from room group and send to WebSocket.
        """
        await self.send(text_data=json.dumps({
            "type": "language_changed",
            "language": event["language"],
            "timestamp": event["timestamp"],
            "source": event.get("source", "telegram")
        }))
    
    @database_sync_to_async
    def user_exists(self, telegram_id):
        """Check if user exists in database"""
        return UserProfile.objects.filter(telegram_id=telegram_id).exists()
    
    @database_sync_to_async
    def get_user_language(self):
        """Get current user language preference"""
        try:
            user = UserProfile.objects.get(telegram_id=self.telegram_id)
            return user.language or 'en'
        except UserProfile.DoesNotExist:
            return 'en'
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return 'en'
    
    @database_sync_to_async
    def update_user_language(self, language_code):
        """Update user language preference"""
        try:
            if language_code not in ['en', 'am', 'om']:
                return False
            
            user = UserProfile.objects.get(telegram_id=self.telegram_id)
            user.language = language_code
            user.save(update_fields=['language'])
            return True
        except UserProfile.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    async def send_current_language(self):
        """Send current language preference to WebSocket"""
        language = await self.get_user_language()
        await self.send(text_data=json.dumps({
            "type": "current_language",
            "language": language,
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    
    URL path: /ws/notifications/<telegram_id>/
    """
    
    async def connect(self):
        self.telegram_id = self.scope["url_route"]["kwargs"]["telegram_id"]
        self.room_name = f"notifications_{self.telegram_id}"
        self.room_group_name = f"notifications_{self.telegram_id}"
        
        # Check if the user exists
        user_exists = await self.user_exists(self.telegram_id)
        if not user_exists:
            logger.warning(f"Connection attempt for non-existent user: {self.telegram_id}")
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Send initial data
        await self.send_initial_data()
        
        logger.info(f"WebSocket connected for user {self.telegram_id}")
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"WebSocket disconnected for user {self.telegram_id} with code {close_code}")
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        
        Expected format: {
            "action": "mark_read",
            "notification_id": "uuid-string"
        }
        """
        try:
            data_json = json.loads(text_data)
            action = data_json.get("action")
            
            if action == "mark_read":
                notification_id = data_json.get("notification_id")
                if notification_id:
                    success = await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        "type": "notification_read",
                        "notification_id": notification_id,
                        "success": success
                    }))
            
            elif action == "subscribe_report":
                report_id = data_json.get("report_id")
                if report_id:
                    # Join a specific report group for updates
                    report_group = f"report_{report_id}"
                    await self.channel_layer.group_add(report_group, self.channel_name)
                    await self.send(text_data=json.dumps({
                        "type": "subscribed",
                        "report_id": report_id,
                    }))
        
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from WebSocket")
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {e}")
    
    async def notification_message(self, event):
        """
        Handle notification message from room group and send to WebSocket.
        """
        # Forward message to WebSocket
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "title": event["title"],
            "message": event["message"],
            "notification_type": event["notification_type"],
            "priority": event["priority"],
            "notification_id": event["notification_id"],
            "timestamp": event["timestamp"],
            "related_report": event.get("related_report"),
            "related_agency": event.get("related_agency"),
        }))
    
    async def report_update(self, event):
        """
        Handle report status update and send to WebSocket.
        """
        # Forward message to WebSocket
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "report_id": event["report_id"],
            "status": event["status"],
            "message": event["message"],
            "timestamp": event["timestamp"],
        }))
    
    @database_sync_to_async
    def user_exists(self, telegram_id):
        """Check if user exists in database"""
        return UserProfile.objects.filter(telegram_id=telegram_id).exists()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        from notifications.models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user__telegram_id=self.telegram_id
            )
            notification.mark_as_read()
            return True
        except (Notification.DoesNotExist, ObjectDoesNotExist):
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    @database_sync_to_async
    def get_user_notifications(self, limit=10):
        """Get recent unread notifications for a user"""
        from notifications.models import Notification
        try:
            user = UserProfile.objects.get(telegram_id=self.telegram_id)
            notifications = Notification.objects.filter(
                user=user,
                is_read=False
            ).order_by('-created_at')[:limit]
            
            return [
                {
                    "id": str(n.id),
                    "title": n.title,
                    "message": n.message,
                    "notification_type": n.notification_type,
                    "priority": n.priority,
                    "timestamp": n.created_at.isoformat(),
                    "related_report": str(n.related_report.id) if n.related_report else None,
                    "related_agency": str(n.related_agency.id) if n.related_agency else None,
                }
                for n in notifications
            ]
        except UserProfile.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    @database_sync_to_async
    def get_user_reports(self, limit=5):
        """Get recent reports for a user"""
        try:
            user = UserProfile.objects.get(telegram_id=self.telegram_id)
            reports = IncidentReport.objects.filter(user=user).order_by('-submitted_at')[:limit]
            
            return [
                {
                    "id": str(r.id),
                    "type": r.type,
                    "status": r.status,
                    "location": r.location,
                    "submitted_at": r.submitted_at.isoformat(),
                }
                for r in reports
            ]
        except UserProfile.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return []
    
    async def send_initial_data(self):
        """Send initial data when WebSocket connects"""
        notifications = await self.get_user_notifications()
        reports = await self.get_user_reports()
        
        await self.send(text_data=json.dumps({
            "type": "initial_data",
            "notifications": notifications,
            "reports": reports,
        }))


class ReportUpdateConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for specific report updates.
    
    URL path: /ws/reports/<report_id>/
    """
    
    async def connect(self):
        self.report_id = self.scope["url_route"]["kwargs"]["report_id"]
        self.room_group_name = f"report_{self.report_id}"
        
        # Check if report exists and if user has access
        access_granted = await self.check_report_access()
        if not access_granted:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Send initial report data
        await self.send_report_data()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket - could be used for specific actions
        related to the report
        """
        pass
    
    async def report_update(self, event):
        """
        Receive report update from group and send to WebSocket
        """
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def check_report_access(self):
        """Check if user has access to this report"""
        # For now, we're not implementing complex authorization
        # In a real app, you'd verify user permissions here
        try:
            return IncidentReport.objects.filter(id=self.report_id).exists()
        except Exception:
            return False
    
    @database_sync_to_async
    def get_report_data(self):
        """Get report data to send when WebSocket connects"""
        try:
            report = IncidentReport.objects.get(id=self.report_id)
            return {
                "id": str(report.id),
                "type": report.type,
                "status": report.status,
                "description": report.description,
                "location": report.location,
                "submitted_at": report.submitted_at.isoformat(),
                "last_updated": report.last_updated.isoformat(),
            }
        except IncidentReport.DoesNotExist:
            return None
    
    async def send_report_data(self):
        """Send report data when WebSocket connects"""
        report_data = await self.get_report_data()
        if report_data:
            await self.send(text_data=json.dumps({
                "type": "report_data",
                "report": report_data,
            })) 