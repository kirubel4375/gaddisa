"""
URL Configuration for Emergency Reporting System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),
    
    # API endpoints
    path('api/v1/accounts/', include('emergency_bot.accounts.urls')),
    path('api/v1/reports/', include('emergency_bot.reports.urls')),
    path('api/v1/agencies/', include('emergency_bot.agencies.urls')),
    path('api/v1/notifications/', include('emergency_bot.notifications.urls')),
    
    # Telegram webhook
    path('telegram/', include('emergency_bot.telegram_bot.urls')),
    
    # Frontend routes for the Telegram Mini App
    path('webapp/', include('emergency_bot.frontend.urls')),
    
    # Redirect root URL to webapp for now
    path('', RedirectView.as_view(url='/webapp/'), name='home'),
]

# Add media and static URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar URLs in development
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns 