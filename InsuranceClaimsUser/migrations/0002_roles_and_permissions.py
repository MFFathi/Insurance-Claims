from django.db import migrations, models

def create_roles_and_permissions(apps, schema_editor):
    Role = apps.get_model('InsuranceClaimsUser', 'Role')
    Permission = apps.get_model('InsuranceClaimsUser', 'Permission')
    User = apps.get_model('InsuranceClaimsUser', 'User')
    
    # Create roles
    admin_role = Role.objects.create(name='Admin')
    finance_role = Role.objects.create(name='Finance')
    user_role = Role.objects.create(name='User')
    
    # Define permissions for each role
    role_permissions = {
        admin_role: {
            'account.view.all': True,
            'account.view.self': True,
            'account.create': True,
            'account.update.all': True,
            'account.update.self': True,
            'account.delete.all': True,
            'account.delete.self': True,
            'records.view.all': True,
            'records.create': True,
            'records.update.all': True,
            'records.delete.all': True
        },
        finance_role: {
            'finance.process': True,
            'finance.approve': True,
            'finance.reject': True,
            'finance.view.all': True,
            'records.view.all': True
        },
        user_role: {
            'claim.create': True,
            'claim.view.self': True,
            'claim.update.self': True,
            'claim.delete.self': True,
            'account.view.self': True,
            'account.update.self': True,
            'account.delete.self': True
        }
    }
    
    # Create permissions for each role
    for role, permissions in role_permissions.items():
        for name, is_allowed in permissions.items():
            Permission.objects.create(
                name=name,
                is_allowed=is_allowed,
                role=role
            )
    
    # Assign Admin role to all superusers
    for user in User.objects.filter(is_superuser=True):
        user.role = admin_role
        user.save()

def remove_roles_and_permissions(apps, schema_editor):
    Role = apps.get_model('InsuranceClaimsUser', 'Role')
    Permission = apps.get_model('InsuranceClaimsUser', 'Permission')
    Role.objects.all().delete()
    Permission.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('InsuranceClaimsUser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ] 