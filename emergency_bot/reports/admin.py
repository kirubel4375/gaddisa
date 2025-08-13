"""
Admin configuration for the reports app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import IncidentReport


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_type_display', 'get_user', 'location_preview', 'status', 'submitted_at')
    list_filter = ('type', 'status', 'submitted_at')
    search_fields = ('id', 'user__telegram_id', 'location', 'description')
    readonly_fields = (
        'id', 'user', 'submitted_at', 'last_updated', 
        'ip_address', 'device_info', 'get_decrypted_description',
        'map_view'
    )
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'type', 'status', 'user')
        }),
        ('Description', {
            'fields': ('get_decrypted_description',)
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude', 'map_view')
        }),
        ('Files', {
            'fields': ('voice_note_url',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'last_updated')
        }),
        ('Audit', {
            'fields': ('ip_address', 'device_info'),
            'classes': ('collapse',)
        }),
    )
    
    def get_type_display(self, obj):
        """Return human-readable incident type."""
        return obj.get_type_display()
    get_type_display.short_description = 'Type'
    get_type_display.admin_order_field = 'type'
    
    def get_user(self, obj):
        """Return link to user profile admin."""
        if obj.user:
            url = reverse('admin:accounts_userprofile_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.telegram_id)
        return '-'
    get_user.short_description = 'User'
    get_user.admin_order_field = 'user__telegram_id'
    
    def location_preview(self, obj):
        """Return truncated location string."""
        if obj.location:
            if len(obj.location) > 30:
                return f"{obj.location[:30]}..."
            return obj.location
        return '-'
    location_preview.short_description = 'Location'
    
    def map_view(self, obj):
        """Return an embedded map view of the location."""
        if obj.latitude and obj.longitude:
            map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={obj.longitude-0.01}%2C{obj.latitude-0.01}%2C{obj.longitude+0.01}%2C{obj.latitude+0.01}&amp;layer=mapnik&amp;marker={obj.latitude}%2C{obj.longitude}"
            return format_html(
                '<iframe width="100%" height="300" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{}"></iframe>'
                '<br/><a href="https://www.openstreetmap.org/?mlat={}&mlon={}#map=15/{}/{}" target="_blank">View on OpenStreetMap</a>',
                map_url, obj.latitude, obj.longitude, obj.latitude, obj.longitude
            )
        return "Location coordinates not provided."
    map_view.short_description = "Map"
    
    def get_decrypted_description(self, obj):
        """Return the decrypted description."""
        if obj.description_encrypted:
            return obj.get_decrypted_description() or "Unable to decrypt description."
        return obj.description or "No description provided."
    get_decrypted_description.short_description = "Description (Decrypted)"
    
    def has_add_permission(self, request):
        """Disable adding reports from admin."""
        return False 