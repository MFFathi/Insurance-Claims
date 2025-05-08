from django.apps import AppConfig
from django.db.models.signals import post_migrate


class InsuranceclaimsuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'InsuranceClaimsUser'

    def ready(self):
        from .models import Role, Permission
        from django.contrib.auth import get_user_model
        User = get_user_model()

        def setup_roles_and_permissions(sender, **kwargs):
            # Define the roles and their permissions
            roles_config = {
                'admin': {
                    'permissions': [
                        'claims.*',
                        'users.*',
                        'roles.*',
                        'permissions.*',
                        'reports.*',
                        'ml.*',  # Admin has full access to ML features
                    ]
                },
                'finance': {
                    'permissions': [
                        'claims.view',
                        'claims.approve',
                        'claims.reject',
                        'reports.view',
                        'billing.view',
                        'billing.create',
                        'billing.edit',
                        'billing.delete',
                        'billing.approve',
                        'billing.reject',
                    ]
                },
                'ai engineer': {
                    'permissions': [
                        'claims.view',
                        'claims.predict',
                        'claims.train',
                        'reports.view',
                        'ml.view',
                        'ml.upload',
                        'ml.update',
                        'ml.delete',
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
                role, created = Role.objects.get_or_create(name=role_name.lower())
                if created:
                    print(f'Created role: {role_name}')
                
                # Set up permissions for the role
                for permission_name in config['permissions']:
                    permission, created = Permission.objects.get_or_create(
                        name=permission_name,
                        role=role,
                        defaults={'is_allowed': True}
                    )
                    if created:
                        print(f'Created permission: {permission_name} for role {role_name}')

            # Assign Admin role to all superusers
            admin_role = Role.objects.get(name='admin')
            for user in User.objects.filter(is_superuser=True):
                if not user.role:
                    user.role = admin_role
                    user.save()
                    print(f'Assigned admin role to superuser: {user.username}')

        # Connect the signal
        post_migrate.connect(setup_roles_and_permissions, sender=self)
