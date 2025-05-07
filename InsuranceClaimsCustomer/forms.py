import pandas as pd
from django import forms
from .models import CustomerClaim
import os

# Load CSV from correct path
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'InsuranceClaimsML', 'Patient_records.csv')
df = pd.read_csv(CSV_PATH)

def get_unique_choices(column_name, fallback="N/A"):
    try:
        values = df[column_name].dropna().unique()
        if len(values) == 0:
            return [(fallback, fallback)]
        return [(v, v) for v in sorted(values)]
    except KeyError:
        return [(fallback, fallback)]

class CustomerClaimForm(forms.ModelForm):
    class Meta:
        model = CustomerClaim
        exclude = ['user']  # ✅ Exclude user so it's not required in the form

    def __init__(self, *args, **kwargs):
        super(CustomerClaimForm, self).__init__(*args, **kwargs)

        dropdown_fields = {
            'AccidentType': 'AccidentType',
            'Injury_Prognosis': 'Injury_Prognosis',
            'Exceptional_Circumstances': 'Exceptional_Circumstances',
            'Minor_Psychological_Injury': 'Minor_Psychological_Injury',
            'Dominant_injury': 'Dominant injury',
            'Whiplash': 'Whiplash',
            'Vehicle_Type': 'Vehicle Type',
            'Weather_Conditions': 'Weather Conditions',
            'Accident_Description': 'Accident Description',
            'Injury_Description': 'Injury Description',
            'Police_Report_Filed': 'Police Report Filed',
            'Witness_Present': 'Witness Present',
            'Gender': 'Gender',
        }

        numeric_fields = [
            'Driver_Age', 'Vehicle_Age', 'Number_of_Passengers',
            'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage',
            'GeneralRest', 'SpecialAdditionalInjury', 'SpecialEarningsLoss',
            'SpecialUsageLoss', 'SpecialMedications', 'SpecialAssetDamage',
            'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed',
            'GeneralUplift', 'SpecialLoanerVehicle', 'SpecialTripCosts',
            'SpecialJourneyExpenses', 'SpecialTherapy'
        ]

        for field in numeric_fields:
            self.fields[field].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': 1})

        # Set calendar input for the two date fields
        self.fields['Accident_Date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['Claim_Date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

        # All other dropdowns populated from CSV
        for field, column in dropdown_fields.items():
            choices = get_unique_choices(column)
            self.fields[field].widget = forms.Select(choices=choices, attrs={'class': 'form-control'})
