from django import forms
from .models import InsuranceClaim

class ClaimForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    Gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Police_Report_Filed = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    Witness_Present = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    Whiplash = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    Exceptional_Circumstances = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    Minor_Psychological_Injury = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = InsuranceClaim
        exclude = ['SettlementValue']
        widgets = {
            'AccidentType': forms.TextInput(attrs={'class': 'form-control'}),
            'Injury_Prognosis': forms.TextInput(attrs={'class': 'form-control'}),
            'SpecialHealthExpenses': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialReduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialOverage': forms.NumberInput(attrs={'class': 'form-control'}),
            'GeneralRest': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialAdditionalInjury': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialEarningsLoss': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialUsageLoss': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialMedications': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialAssetDamage': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialRehabilitation': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialFixes': forms.NumberInput(attrs={'class': 'form-control'}),
            'GeneralFixed': forms.NumberInput(attrs={'class': 'form-control'}),
            'GeneralUplift': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialLoanerVehicle': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialTripCosts': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialJourneyExpenses': forms.NumberInput(attrs={'class': 'form-control'}),
            'SpecialTherapy': forms.NumberInput(attrs={'class': 'form-control'}),
            'Dominant_injury': forms.TextInput(attrs={'class': 'form-control'}),
            'Vehicle_Type': forms.TextInput(attrs={'class': 'form-control'}),
            'Weather_Conditions': forms.TextInput(attrs={'class': 'form-control'}),
            'Accident_Date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Claim_Date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Vehicle_Age': forms.NumberInput(attrs={'class': 'form-control'}),
            'Driver_Age': forms.NumberInput(attrs={'class': 'form-control'}),
            'Number_of_Passengers': forms.NumberInput(attrs={'class': 'form-control'}),
            'Accident_Description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'Injury_Description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
