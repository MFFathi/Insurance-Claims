from django.db import migrations

def create_finance_role(apps, schema_editor):
    Role = apps.get_model('InsuranceClaimsUser', 'Role')
    Permission = apps.get_model('InsuranceClaimsUser', 'Permission')
    
    # Create Finance role if it doesn't exist
    finance_role, created = Role.objects.get_or_create(name='Finance')
    
    # Add permissions for Finance role
    permissions = [
        # Claim management permissions
        ('claim.view.all', True),
        ('claim.create', True),
        ('claim.update.all', True),
        ('claim.delete.all', True),
        
        # Payment management permissions
        ('payment.view.all', True),
        ('payment.create', True),
        ('payment.update.all', True),
        ('payment.delete.all', True),
        
        # Report permissions
        ('report.view.all', True),
        ('report.create', True),
        
        # Profile management permissions
        ('account.view.self', True),
        ('account.update.self', True),
        
        # Limited user management permissions
        ('account.view.all', True),
        ('account.create', False),
        ('account.update.all', False),
        ('account.delete.all', False),
        
        # No role management permissions
        ('role.view.all', False),
        ('role.create', False),
        ('role.update.all', False),
        ('role.delete.all', False),
    ]
    
    for perm_name, is_allowed in permissions:
        try:
            # Try to get existing permission
            existing_perm = Permission.objects.get(name=perm_name)
            # Update the permission's role if it exists
            existing_perm.role = finance_role
            existing_perm.is_allowed = is_allowed
            existing_perm.save()
        except Permission.DoesNotExist:
            # Create new permission if it doesn't exist
            Permission.objects.create(
                name=perm_name,
                role=finance_role,
                is_allowed=is_allowed
            )

def remove_finance_role(apps, schema_editor):
    Role = apps.get_model('InsuranceClaimsUser', 'Role')
    Role.objects.filter(name='Finance').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('InsuranceClaimsUser', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_finance_role, remove_finance_role),
    ] 