from django.db import models

class InsuranceClaim(models.Model):
    accident_type = models.CharField(max_length=255)
    injury_prognosis = models.CharField(max_length=255)
    # Add all the other fields you need from your dataset...
    settlement_value = models.FloatField()

    def __str__(self):
        return f"Claim - {self.accident_type} - {self.settlement_value}"


class CustomerClaim(models.Model):
    AccidentType = models.CharField(max_length=100)
    Injury_Prognosis = models.CharField(max_length=100)
    SpecialHealthExpenses = models.FloatField()
    SpecialReduction = models.FloatField()
    SpecialOverage = models.FloatField()
    GeneralRest = models.FloatField()
    SpecialAdditionalInjury = models.FloatField()
    SpecialEarningsLoss = models.FloatField()
    SpecialUsageLoss = models.FloatField()
    SpecialMedications = models.FloatField()
    SpecialAssetDamage = models.FloatField()
    SpecialRehabilitation = models.FloatField()
    SpecialFixes = models.FloatField()
    GeneralFixed = models.FloatField()
    GeneralUplift = models.FloatField()
    SpecialLoanerVehicle = models.FloatField()
    SpecialTripCosts = models.FloatField()
    SpecialJourneyExpenses = models.FloatField()
    SpecialTherapy = models.FloatField()
    Exceptional_Circumstances = models.CharField(max_length=100)
    Minor_Psychological_Injury = models.CharField(max_length=100)
    Dominant_injury = models.CharField(max_length=100)
    Whiplash = models.CharField(max_length=100)
    Vehicle_Type = models.CharField(max_length=100)
    Weather_Conditions = models.CharField(max_length=100)
    Accident_Date = models.DateField()
    Claim_Date = models.DateField()
    Vehicle_Age = models.IntegerField()
    Driver_Age = models.IntegerField()
    Number_of_Passengers = models.IntegerField()
    Accident_Description = models.TextField()
    Injury_Description = models.TextField()
    Police_Report_Filed = models.CharField(max_length=3)
    Witness_Present = models.CharField(max_length=3)
    Gender = models.CharField(max_length=10)
