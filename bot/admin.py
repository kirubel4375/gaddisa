from django.contrib import admin
from .models import Location, Service, UserRequestLog

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'location', 'phone_number')
    list_filter = ('service_type', 'location')
    search_fields = ('name',)

@admin.register(UserRequestLog)
class UserRequestLogAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'command', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('chat_id', 'command')
