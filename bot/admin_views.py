from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    Location, Service, UserRequestLog, Role, Permission,
    RolePermission, UserRole, SystemReport
)

def has_permission(user, permission_name):
    """Check if user has specific permission through their roles"""
    user_roles = UserRole.objects.filter(user=user)
    for user_role in user_roles:
        role_permissions = RolePermission.objects.filter(
            role=user_role.role,
            permission__name=permission_name
        )
        if role_permissions.exists():
            return True
    return False

def permission_required(permission_name):
    """Decorator to check if user has required permission"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not has_permission(request.user, permission_name):
                return JsonResponse({
                    'error': 'You do not have permission to perform this action'
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def admin_dashboard(request):
    """Main admin dashboard view"""
    if not has_permission(request.user, 'view_dashboard'):
        return redirect('login')
    
    # Get recent incidents
    recent_incidents = UserRequestLog.objects.order_by('-timestamp')[:10]
    
    # Get service statistics
    service_stats = Service.objects.values('service_type').annotate(
        count=Count('id')
    )
    
    # Get user statistics
    user_stats = {
        'total_users': User.objects.count(),
        'active_users': UserRequestLog.objects.values('chat_id').distinct().count(),
    }
    
    context = {
        'recent_incidents': recent_incidents,
        'service_stats': service_stats,
        'user_stats': user_stats,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@permission_required('manage_services')
def manage_services(request):
    """View to manage emergency services"""
    services = Service.objects.all()
    locations = Location.objects.all()
    
    if request.method == 'POST':
        # Handle service updates
        service_id = request.POST.get('service_id')
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            service.name = request.POST.get('name')
            service.description = request.POST.get('description')
            service.phone_number = request.POST.get('phone_number')
            service.save()
        else:
            # Create new service
            Service.objects.create(
                location_id=request.POST.get('location'),
                service_type=request.POST.get('service_type'),
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                phone_number=request.POST.get('phone_number')
            )
        return redirect('manage_services')
    
    return render(request, 'admin/manage_services.html', {
        'services': services,
        'locations': locations
    })

@login_required
@permission_required('view_reports')
def generate_report(request):
    """Generate system reports"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Generate report data based on type
        report_data = {
            'incidents': UserRequestLog.objects.filter(
                timestamp__range=[start_date, end_date]
            ).count(),
            'services_used': Service.objects.filter(
                userrequestlog__timestamp__range=[start_date, end_date]
            ).distinct().count(),
            'active_users': UserRequestLog.objects.filter(
                timestamp__range=[start_date, end_date]
            ).values('chat_id').distinct().count(),
        }
        
        # Create report
        report = SystemReport.objects.create(
            title=f"{report_type} Report - {start_date} to {end_date}",
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            generated_by=request.user,
            report_data=report_data
        )
        
        return JsonResponse({
            'success': True,
            'report_id': report.id
        })
    
    return render(request, 'admin/generate_report.html')

@login_required
@permission_required('manage_roles')
def manage_roles(request):
    """Manage user roles and permissions"""
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    user_roles = UserRole.objects.select_related('user', 'role')
    
    if request.method == 'POST':
        # Handle role assignments
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        
        if user_id and role_id:
            UserRole.objects.create(
                user_id=user_id,
                role_id=role_id,
                assigned_by=request.user
            )
        return redirect('manage_roles')
    
    return render(request, 'admin/manage_roles.html', {
        'roles': roles,
        'permissions': permissions,
        'user_roles': user_roles
    })

@login_required
@permission_required('manage_services')
def service_api(request, service_id):
    """API endpoint for service operations"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': service.id,
            'name': service.name,
            'service_type': service.service_type,
            'location': service.location.id,
            'description': service.description,
            'phone_number': service.phone_number
        })
    
    elif request.method == 'DELETE':
        service.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@permission_required('manage_roles')
def role_api(request, role_id):
    """API endpoint for role operations"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'GET':
        permissions = RolePermission.objects.filter(role=role).values_list('permission_id', flat=True)
        return JsonResponse({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions': list(permissions)
        })
    
    elif request.method == 'DELETE':
        role.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@permission_required('manage_roles')
def user_role_api(request, user_role_id):
    """API endpoint for user role operations"""
    user_role = get_object_or_404(UserRole, id=user_role_id)
    
    if request.method == 'DELETE':
        user_role.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@permission_required('manage_roles')
def add_role(request):
    """API endpoint for adding new roles"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        permissions = request.POST.getlist('permissions')
        
        role = Role.objects.create(
            name=name,
            description=description
        )
        
        # Add permissions
        for permission_id in permissions:
            RolePermission.objects.create(
                role=role,
                permission_id=permission_id
            )
        
        return JsonResponse({
            'success': True,
            'role_id': role.id
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@permission_required('manage_roles')
def edit_role(request):
    """API endpoint for editing roles"""
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        permissions = request.POST.getlist('permissions')
        
        role = get_object_or_404(Role, id=role_id)
        role.name = name
        role.description = description
        role.save()
        
        # Update permissions
        RolePermission.objects.filter(role=role).delete()
        for permission_id in permissions:
            RolePermission.objects.create(
                role=role,
                permission_id=permission_id
            )
        
        return JsonResponse({
            'success': True,
            'role_id': role.id
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405) 