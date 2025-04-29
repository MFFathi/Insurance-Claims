from django.core.management.base import BaseCommand
from InsuranceClaimsUser.models import Role

class Command(BaseCommand):
    help = 'Creates default roles in the database'

    def handle(self, *args, **kwargs):
        roles = ['customer', 'admin', 'ai engineer', 'finance']
        
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully created/verified role: {role_name}')) 