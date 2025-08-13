"""
Admin configuration for the accounts app.
"""

from django.contrib import admin
from django.utils import timezone
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'language', 'last_active', 'has_consent', 'time_since_active')
    list_filter = ('language', 'data_consent')
    search_fields = ('telegram_id',)
    readonly_fields = ('telegram_id', 'last_active', 'created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('telegram_id', 'language')
        }),
        ('Activity', {
            'fields': ('last_active', 'created_at', 'updated_at')
        }),
        ('GDPR Compliance', {
            'fields': ('data_consent', 'consent_date')
        }),
    )
    
    def has_consent(self, obj):
        """Return whether user has given consent."""
        return obj.data_consent
    has_consent.boolean = True
    
    def time_since_active(self, obj):
        """Return time since last activity."""
        if not obj.last_active:
            return "Never"
        
        delta = timezone.now() - obj.last_active
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "Just now" 