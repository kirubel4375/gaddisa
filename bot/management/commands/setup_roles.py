from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bot.models import Role, Permission, RolePermission, UserRole

class Command(BaseCommand):
    help = 'Sets up initial roles and permissions for the admin dashboard'

    def handle(self, *args, **kwargs):
        # Create permissions
        permissions = {
            'view_dashboard': 'Can view admin dashboard',
            'manage_services': 'Can manage emergency services',
            'view_reports': 'Can view and generate reports',
            'manage_roles': 'Can manage user roles and permissions',
        }
        
        created_permissions = {}
        for name, description in permissions.items():
            permission, created = Permission.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            created_permissions[name] = permission
            if created:
                self.stdout.write(f'Created permission: {name}')
        
        # Create roles
        roles = {
            'super_admin': {
                'description': 'Super Administrator with full access',
                'permissions': list(created_permissions.keys())
            },
            'service_manager': {
                'description': 'Can manage emergency services',
                'permissions': ['view_dashboard', 'manage_services']
            },
            'report_viewer': {
                'description': 'Can view and generate reports',
                'permissions': ['view_dashboard', 'view_reports']
            }
        }
        
        for name, data in roles.items():
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={'description': data['description']}
            )
            
            if created:
                self.stdout.write(f'Created role: {name}')
                
                # Add permissions to role
                for perm_name in data['permissions']:
                    RolePermission.objects.create(
                        role=role,
                        permission=created_permissions[perm_name]
                    )
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'  # Change this in production!
            )
            self.stdout.write('Created superuser: admin')
            
            # Assign super_admin role to admin user
            admin_user = User.objects.get(username='admin')
            super_admin_role = Role.objects.get(name='super_admin')
            UserRole.objects.create(
                user=admin_user,
                role=super_admin_role,
                assigned_by=admin_user
            )
            self.stdout.write('Assigned super_admin role to admin user')
        
        self.stdout.write(self.style.SUCCESS('Successfully set up roles and permissions')) 