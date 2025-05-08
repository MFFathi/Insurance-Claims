from django.core.management.base import BaseCommand
from InsuranceClaimsUser.models import Role, Permission
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Sets up initial roles and permissions for the application'

    def handle(self, *args, **options):
        # Define the roles and their permissions
        roles_config = {
            'admin': {
                'permissions': [
                    'claims.*',
                    'users.*',
                    'roles.*',
                    'permissions.*',
                    'reports.*',
                ]
            },
            'finance': {
                'permissions': [
                    'claims.view',
                    'claims.approve',
                    'claims.reject',
                    'reports.view',
                ]
            },
            'ai engineer': {
                'permissions': [
                    'claims.view',
                    'claims.predict',
                    'claims.train',
                    'reports.view',
                ]
            },
            'customer': {
                'permissions': [
                    'claims.view',
                    'claims.create',
                    'claims.edit',
                ]
            }
        }

        # Create roles and their permissions
        for role_name, config in roles_config.items():
            # Create Django group
            group, group_created = Group.objects.get_or_create(name=role_name.lower())
            if group_created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
            
            # Create custom role
            role, role_created = Role.objects.get_or_create(name=role_name.lower())
            if role_created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))
            
            # Set up permissions for the role
            for permission_name in config['permissions']:
                permission, created = Permission.objects.get_or_create(
                    name=permission_name,
                    role=role,
                    defaults={'is_allowed': True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created permission: {permission_name} for role {role_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully set up initial roles and permissions')) 