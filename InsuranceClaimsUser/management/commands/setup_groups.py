from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from InsuranceClaimsUser.models import User, Role, Permission as CustomPermission

class Command(BaseCommand):
    help = 'Sets up the role groups and their permissions'

    def handle(self, *args, **options):
        # Create roles
        roles = {
            'admin': {
                'permissions': ['view', 'add', 'change', 'delete'],
                'description': 'Full access to all features'
            },
            'customer': {
                'permissions': ['view'],
                'description': 'Can view and submit claims'
            },
            'finance': {
                'permissions': ['view', 'change'],
                'description': 'Can view and process claims'
            },
            'ai_engineer': {
                'permissions': ['view', 'change'],
                'description': 'Can view claims and access AI features'
            }
        }

        # Create Django groups and custom roles
        for role_name, role_data in roles.items():
            # Create Django group
            group, created = Group.objects.get_or_create(name=role_name)
            
            # Create custom role
            custom_role, created = Role.objects.get_or_create(name=role_name)
            
            # Add permissions to the group
            for permission in role_data['permissions']:
                # Add Django permissions
                content_type = ContentType.objects.get_for_model(User)
                permission_codename = f'{permission}_user'
                permission_obj, created = Permission.objects.get_or_create(
                    codename=permission_codename,
                    content_type=content_type
                )
                group.permissions.add(permission_obj)
                
                # Add custom permissions
                CustomPermission.objects.get_or_create(
                    name=permission,
                    role=custom_role,
                    is_allowed=True
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully created {role_name} role'))

        self.stdout.write(self.style.SUCCESS('Successfully set up all roles and permissions')) 