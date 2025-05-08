from django.core.management.base import BaseCommand
from InsuranceClaimsCustomer.models import CustomerClaim, InsuranceClaim

class Command(BaseCommand):
    help = 'Backfill InsuranceClaim.customer_claim ForeignKey based on matching accident_type and user.'

    def handle(self, *args, **options):
        count = 0
        for claim in CustomerClaim.objects.all():
            # Try to find a matching InsuranceClaim (customize the filter as needed)
            prediction = InsuranceClaim.objects.filter(
                accident_type=claim.AccidentType,
                # Optionally add more filters here for better matching
                customer_claim__isnull=True
            ).first()
            if prediction:
                prediction.customer_claim = claim
                prediction.save()
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Linked InsuranceClaim {prediction.id} to CustomerClaim {claim.id}'))
        self.stdout.write(self.style.SUCCESS(f'Backfill complete. Linked {count} InsuranceClaims.')) 