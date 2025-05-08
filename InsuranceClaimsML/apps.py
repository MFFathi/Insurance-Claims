from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os

class InsuranceclaimsmlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'InsuranceClaimsML'
    path = os.path.abspath(os.path.dirname(__file__))  # Ensures consistent app path

    def ready(self):
        from InsuranceClaimsUser.models import Role, Permission

        def setup_ml_permissions(sender, **kwargs):
            # Ensure AI Engineer role has ML permissions
            ai_engineer_role = Role.objects.filter(name='ai engineer').first()
            if ai_engineer_role:
                ml_permissions = [
                    'ml.view',
                    'ml.upload',
                    'ml.update',
                    'ml.delete',
                ]
                
                for perm_name in ml_permissions:
                    permission, created = Permission.objects.get_or_create(
                        name=perm_name,
                        role=ai_engineer_role,
                        defaults={'is_allowed': True}
                    )
                    if created:
                        print(f'Created ML permission: {perm_name} for AI Engineer role')

        # Connect the signal
        post_migrate.connect(setup_ml_permissions, sender=self)
