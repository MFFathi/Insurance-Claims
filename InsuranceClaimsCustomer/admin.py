from django.contrib import admin
from .models import InsuranceClaim

# Prevent double registration
from django.contrib.admin.sites import AlreadyRegistered

try:
    @admin.register(InsuranceClaim)
    class InsuranceClaimAdmin(admin.ModelAdmin):
        list_display = ('id', 'Gender', 'Accident_Date', 'Claim_Date')
        search_fields = ('Gender', 'AccidentType')
        list_filter = ('Gender', 'Accident_Date')

except AlreadyRegistered:
    pass
