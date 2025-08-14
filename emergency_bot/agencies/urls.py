"""URL configuration for the agencies app."""

from django.urls import path
from . import views

urlpatterns = [
    # API endpoints for agencies
    path('all/', views.all_agencies, name='api_all_agencies'),
    path('nearby/', views.nearby_agencies, name='api_nearby_agencies'),
    path('search/', views.search_agencies, name='api_search_agencies'),
    path('locations/zones/', views.get_zones, name='api_get_zones'),
    path('locations/woredas/', views.get_woredas, name='api_get_woredas'),
    path('locations/kebeles/', views.get_kebeles, name='api_get_kebeles'),
] 