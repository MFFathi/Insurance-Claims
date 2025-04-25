from django.db import models

class RecordManager(models.Manager):
    def sort_by(self, field_name, descending=False):
        if descending:
            field_name = f"-{field_name}"
        return self.order_by(field_name)

class Record(models.Model):
    record_id = models.AutoField(primary_key=True)
    record_type = models.CharField(max_length=150, blank=True, null=True)

    # Financial & Medical Claims
    settlement_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    accident_type = models.CharField(max_length=150, blank=True, null=True)
    injury_prognosis = models.CharField(max_length=150, blank=True, null=True)
    special_health_expenses = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_reduction = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_overage = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    general_rest = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_additional_injury = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_earnings_loss = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_usage_loss = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_medications = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_asset_damage = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_rehabilitation = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_fixes = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    general_fixed = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    general_uplift = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_loaner_vehicle = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_trip_costs = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_journey_expenses = models.CharField(max_length=150, blank=True, null=True)
    special_therapy = models.CharField(max_length=150, blank=True, null=True)

    # Injury and Legal Reports
    exceptional_circumstances = models.BooleanField(default=False)
    minor_psychological_injury = models.BooleanField(default=False)
    dominant_injury = models.CharField(max_length=150, blank=True, null=True)
    whiplash = models.BooleanField(default=False)

    # Vehicle and Weather Conditions
    vehicle_type = models.CharField(max_length=150, blank=True, null=True)
    weather_conditions = models.CharField(max_length=150, blank=True, null=True)
    vehicle_age = models.IntegerField(blank=True, null=True)
    driver_age = models.IntegerField(blank=True, null=True)
    number_of_passengers = models.IntegerField(blank=True, null=True)

    # Descriptions
    accident_description = models.TextField(blank=True, null=True)
    injury_description = models.TextField(blank=True, null=True)

    # Legal and Reporting
    police_report_filed = models.BooleanField(default=False)
    witness_present = models.BooleanField(default=False)

    # Personal Information
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    # Dates
    accident_date = models.DateField(blank=True, null=True)
    claim_date = models.DateField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    last_modified_date = models.DateField(auto_now=True)

    # Claim Status
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['accident_date']),
        ]

    objects = RecordManager()

    def __str__(self):
        return f"Record #{self.record_id} - {self.record_type}"
