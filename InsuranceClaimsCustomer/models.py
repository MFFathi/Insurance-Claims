from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    # Accident Details
    AccidentType = models.CharField(max_length=100)
    Injury_Prognosis = models.CharField(max_length=100)
    Exceptional_Circumstances = models.CharField(max_length=3)
    Minor_Psychological_Injury = models.CharField(max_length=3)
    Dominant_injury = models.CharField(max_length=100)
    Whiplash = models.CharField(max_length=3)
    Vehicle_Type = models.CharField(max_length=100)
    Weather_Conditions = models.CharField(max_length=100)
    Accident_Description = models.TextField()
    Injury_Description = models.TextField()
    Police_Report_Filed = models.CharField(max_length=3)
    Witness_Present = models.CharField(max_length=3)
    Gender = models.CharField(max_length=10)
    
    # Numeric Fields
    Driver_Age = models.IntegerField()
    Vehicle_Age = models.IntegerField()
    Number_of_Passengers = models.IntegerField()
    SpecialHealthExpenses = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialReduction = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialOverage = models.DecimalField(max_digits=10, decimal_places=2)
    GeneralRest = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialAdditionalInjury = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialEarningsLoss = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialUsageLoss = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialMedications = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialAssetDamage = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialRehabilitation = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialFixes = models.DecimalField(max_digits=10, decimal_places=2)
    GeneralFixed = models.DecimalField(max_digits=10, decimal_places=2)
    GeneralUplift = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialLoanerVehicle = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialTripCosts = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialJourneyExpenses = models.DecimalField(max_digits=10, decimal_places=2)
    SpecialTherapy = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Date Fields
    Accident_Date = models.DateField()
    Claim_Date = models.DateField()
    
    # Prediction Field
    predicted_settlement = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Claim by {self.user.username} on {self.Claim_Date}"

class InsuranceClaim(models.Model):
    customer_claim = models.ForeignKey(CustomerClaim, on_delete=models.CASCADE, related_name='insurance_claims', null=True, blank=True)
    accident_type = models.CharField(max_length=100)
    injury_prognosis = models.CharField(max_length=100)
    settlement_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Claim {self.id} - {self.accident_type} - ${self.settlement_value}"

class Feedback(models.Model):
    claim = models.ForeignKey('CustomerClaim', on_delete=models.CASCADE, related_name='feedbacks')
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    submission_date = models.DateTimeField(auto_now_add=True)
