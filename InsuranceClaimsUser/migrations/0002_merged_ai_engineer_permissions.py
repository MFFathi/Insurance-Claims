from django.db import migrations

def create_ai_engineer_role_and_permissions(apps, schema_editor):
    Role = apps.get_model('InsuranceClaimsUser', 'Role')
    Permission = apps.get_model('InsuranceClaimsUser', 'Permission')
    
    # Create AI Engineer role
    ai_engineer_role, created = Role.objects.get_or_create(name='AI Engineer')
    
    # Define all permissions that AI Engineer should have
    permissions = [
        ('records.view', True),
        ('records.view.all', True),
        ('records.list', True),
        ('ml.upload', True),
        ('ml.update', True),
        ('ml.view', True),
        ('ml.delete', True),
    ]
    
    # Create all permissions
    for perm_name, is_allowed in permissions:
        Permission.objects.get_or_create(
            role=ai_engineer_role,
            name=perm_name,
            defaults={'is_allowed': is_allowed}
        )

def remove_ai_engineer_role_and_permissions(apps, schema_editor):
    Role = apps.get_model('InsuranceClaimsUser', 'Role')
    Permission = apps.get_model('InsuranceClaimsUser', 'Permission')
    
    # Get the AI Engineer role
    ai_engineer_role = Role.objects.get(name='AI Engineer')
    
    # Remove all permissions associated with the role
    Permission.objects.filter(role=ai_engineer_role).delete()
    
    # Remove the role itself
    ai_engineer_role.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('InsuranceClaimsUser', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_ai_engineer_role_and_permissions,
            remove_ai_engineer_role_and_permissions
        ),
    ] 