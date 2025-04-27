from django.contrib import admin
from .models import InsuranceClaim, CustomerClaim

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ['accident_type', 'injury_prognosis', 'settlement_value']
    search_fields = ['accident_type', 'injury_prognosis']

@admin.register(CustomerClaim)
class CustomerClaimAdmin(admin.ModelAdmin):
    list_display = ['AccidentType', 'Driver_Age', 'Vehicle_Age', 'Gender']
    search_fields = ['AccidentType', 'Gender']
    list_filter = ['Gender']
