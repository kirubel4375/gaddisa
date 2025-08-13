from django.db import models
import uuid


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('report_status', 'Report Status Update'),
        ('nearby_agency', 'Nearby Agency Alert'),
        ('system', 'System Notification'),
        ('safety_tip', 'Safety Tip'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Optional related objects
    related_report = models.ForeignKey('reports.IncidentReport', on_delete=models.SET_NULL, 
                                       null=True, blank=True, related_name='notifications')
    related_agency = models.ForeignKey('agencies.Agency', on_delete=models.SET_NULL, 
                                       null=True, blank=True, related_name='notifications')
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user} - {self.created_at}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.is_sent = True
        self.save(update_fields=['is_sent'])
    
    @property
    def time_since_creation(self):
        """Get time since notification was created"""
        from django.utils import timezone
        return timezone.now() - self.created_at


class NotificationChannel(models.Model):
    """Configuration for notification delivery channels"""
    CHANNEL_TYPES = (
        ('telegram', 'Telegram Message'),
        ('websocket', 'WebSocket Push'),
        ('email', 'Email'),
    )
    
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, related_name='notification_channels')
    channel_type = models.CharField(max_length=15, choices=CHANNEL_TYPES)
    is_enabled = models.BooleanField(default=True)
    
    # Channel-specific settings
    telegram_chat_id = models.CharField(max_length=100, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Notification Channel"
        verbose_name_plural = "Notification Channels"
        unique_together = ('user', 'channel_type')
        
    def __str__(self):
        return f"{self.get_channel_type_display()} channel for {self.user}" 