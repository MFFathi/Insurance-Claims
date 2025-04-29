from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from InsuranceClaimsUser.models import User, Role

# Define the canonical role names (all lowercase)
CANONICAL_ROLES = [
    'admin',
    'finance',
    'ai engineer',
    'customer',
]

class Command(BaseCommand):
    help = 'Standardize role and group names to lowercase and sync Django groups with custom Role model.'

    def handle(self, *args, **options):
        # Standardize role names to lowercase
        for role in Role.objects.all():
            canonical = role.name.strip().lower()
            if canonical not in CANONICAL_ROLES:
                self.stdout.write(self.style.WARNING(f"Unknown role '{role.name}', setting to lowercase anyway."))
            if role.name != canonical:
                self.stdout.write(f"Updating role '{role.name}' to '{canonical}'")
                role.name = canonical
                role.save()

        # Standardize group names to lowercase
        for group in Group.objects.all():
            canonical = group.name.strip().lower()
            if group.name != canonical:
                self.stdout.write(f"Renaming group '{group.name}' to '{canonical}'")
                group.name = canonical
                group.save()

        # Sync groups for each user
        for user in User.objects.all():
            if not user.role:
                self.stdout.write(f"User {user.username} has no role, skipping.")
                continue
            role_name = user.role.name.strip().lower()
            # Ensure group exists
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f"Created group '{role_name}'")
            # Add user to the group if not already
            if not user.groups.filter(name=role_name).exists():
                user.groups.add(group)
                self.stdout.write(f"Added user '{user.username}' to group '{role_name}'")
            # Remove user from groups that don't match their role
            for g in user.groups.exclude(name=role_name):
                user.groups.remove(g)
                self.stdout.write(f"Removed user '{user.username}' from group '{g.name}'")

        self.stdout.write(self.style.SUCCESS('Roles and groups have been standardized to lowercase and synced.')) 