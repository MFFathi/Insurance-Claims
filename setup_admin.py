from django.contrib.auth import get_user_model
from InsuranceClaimsUser.models import Role, Permission

def setup_admin():
    # Create Admin role if it doesn't exist
    admin_role, created = Role.objects.get_or_create(name='Admin')
    
    # Create necessary permissions for Admin role
    permissions = [
        'view_user',
        'add_user',
        'change_user',
        'delete_user',
        'view_claim',
        'add_claim',
        'change_claim',
        'delete_claim',
        'view_customer',
        'add_customer',
        'change_customer',
        'delete_customer',
        'view_policy',
        'add_policy',
        'change_policy',
        'delete_policy',
    ]
    
    # Create permissions and assign to Admin role
    for perm_name in permissions:
        Permission.objects.get_or_create(
            name=perm_name,
            is_allowed=True,
            role=admin_role
        )
    
    # Assign Admin role to all superusers
    User = get_user_model()
    for user in User.objects.filter(is_superuser=True):
        user.role = admin_role
        user.save()
    
    print("Admin role and permissions have been set up successfully!")

if __name__ == '__main__':
    setup_admin() 