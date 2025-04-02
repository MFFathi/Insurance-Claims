from django.db import models

class Claim(models.Model):
    INJURY_CHOICES = [
        ('minor', 'Minor Injury'),
        ('moderate', 'Moderate Injury'),
        ('severe', 'Severe Injury'),
    ]

    EARNINGS_CHOICES = [
        ('low', 'Less than $1,000'),
        ('medium', '$1,000 - $5,000'),
        ('high', 'More than $5,000'),
    ]

    EXPENSES_CHOICES = [
        ('none', 'None'),
        ('medical', 'Medical Costs'),
        ('legal', 'Legal Fees'),
    ]

    injury = models.CharField(max_length=50, choices=INJURY_CHOICES)
    earnings = models.CharField(max_length=50, choices=EARNINGS_CHOICES)
    expenses = models.CharField(max_length=50, choices=EXPENSES_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.injury} | {self.earnings} | {self.expenses}"
