"""
Admin configuration for the agencies app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Agency


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_type_display', 'region', 'zone', 'phone', 'verified', 'active')
    list_filter = ('type', 'verified', 'active', 'region', 'zone')
    search_fields = ('name', 'address', 'phone', 'email', 'region', 'zone', 'woreda', 'kebele')
    prepopulated_fields = {'slug': ('name', 'region')}
    readonly_fields = ('map_view', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'type', 'description')
        }),
        ('Location', {
            'fields': (
                'region', 'zone', 'woreda', 'kebele',
                'address', 'latitude', 'longitude', 'map_view'
            )
        }),
        ('Contact', {
            'fields': ('phone', 'alt_phone', 'email')
        }),
        ('Operational Details', {
            'fields': ('hours_of_operation', 'services')
        }),
        ('Status', {
            'fields': ('verified', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_type_display(self, obj):
        """Return human-readable agency type."""
        return obj.get_type_display()
    get_type_display.short_description = 'Type'
    get_type_display.admin_order_field = 'type'
    
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
    
    def save_model(self, request, obj, form, change):
        """Auto-generate slug if not provided."""
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(f"{obj.name}-{obj.region}")
        super().save_model(request, obj, form, change) 