from django.apps import AppConfig
import os

class InsuranceclaimsmlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'InsuranceClaimsML'
    path = os.path.abspath(os.path.dirname(__file__))  # Ensures consistent app path
