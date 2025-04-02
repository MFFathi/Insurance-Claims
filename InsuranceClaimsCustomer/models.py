from django.db import models

class ClaimEntry(models.Model):
    accident_type = models.CharField(max_length=100)
    injury_prognosis = models.TextField()
    expense = models.DecimalField(max_digits=10, decimal_places=2)

    # Auto-injected fields when "Add" button is used
    SpecialHealthExpenses = models.JSONField(default=dict)
