from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = [
            'record_type', 'status', 'accident_date', 'claim_date',
            'settlement_value', 'special_health_expenses', 'accident_type',
            'injury_prognosis', 'vehicle_type', 'vehicle_age', 'driver_age',
            'accident_description', 'injury_description', 'exceptional_circumstances',
            'minor_psychological_injury', 'whiplash', 'police_report_filed'
        ]
        widgets = {
            'accident_date': forms.DateInput(attrs={'type': 'date'}),
            'claim_date': forms.DateInput(attrs={'type': 'date'}),
            'accident_description': forms.Textarea(attrs={'rows': 3}),
            'injury_description': forms.Textarea(attrs={'rows': 3}),
        } 