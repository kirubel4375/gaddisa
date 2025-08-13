"""
URL patterns for the frontend app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    path('agencies/', views.agencies, name='agencies'),
    path('agencies.html', views.agencies, name='agencies_html'),
    path('report/', views.report, name='report'),
    path('report.html', views.report, name='report_html'),
    path('profile/', views.profile, name='profile'),
    path('profile.html', views.profile, name='profile_html'),
    path('api/submit-report/', views.submit_report, name='submit_report'),
    path('submit-report/', views.submit_report, name='submit_report_direct'),
    path('api/upload-voice-note/', views.upload_voice_note, name='upload_voice_note'),
    path('api/frontend/get-user-language/', views.get_user_language, name='get_user_language'),
    path('api/frontend/update-language/', views.update_language, name='update_language'),
    path('api/frontend/check-language-sync/', views.check_language_sync, name='check_language_sync'),
    path('api/frontend/save-location/', views.save_location, name='save_location'),
    path('api/frontend/get-location-status/', views.get_location_status, name='get_location_status'),
] 