from django.urls import path
from . import views, admin_views

urlpatterns = [
    # Bot URLs
    path('webhook/', views.webhook, name='webhook'),
    path('set-webhook/', views.set_webhook, name='set_webhook'),
    
    # Custom Admin Dashboard URLs
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/services/', admin_views.manage_services, name='manage_services'),
    path('dashboard/reports/', admin_views.generate_report, name='generate_report'),
    path('dashboard/roles/', admin_views.manage_roles, name='manage_roles'),
    
    # API endpoints for admin functionality
    path('api/services/<int:service_id>/', admin_views.service_api, name='service_api'),
    path('api/roles/<int:role_id>/', admin_views.role_api, name='role_api'),
    path('api/user-roles/<int:user_role_id>/', admin_views.user_role_api, name='user_role_api'),
    path('api/add-role/', admin_views.add_role, name='add_role'),
    path('api/edit-role/', admin_views.edit_role, name='edit_role'),
] 