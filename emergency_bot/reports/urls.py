"""
URL configuration for the reports app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'incident-reports', views.IncidentReportViewSet)

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
] 