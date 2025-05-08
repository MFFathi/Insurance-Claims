from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        numeric_fields = [
            'settlement_value', 'special_health_expenses', 'special_reduction', 'special_overage',
            'general_rest', 'special_additional_injury', 'special_earnings_loss', 'special_usage_loss',
            'special_medications', 'special_asset_damage', 'special_rehabilitation', 'special_fixes',
            'general_fixed', 'general_uplift', 'special_loaner_vehicle', 'special_trip_costs',
            'vehicle_age', 'driver_age', 'number_of_passengers'
        ]
        for field in numeric_fields:
            if field in self.fields:
                self.fields[field].min_value = 0
                self.fields[field].widget.attrs['min'] = 0

    class Meta:
        model = Record
        fields = [
            'record_type', 'status', 'accident_date', 'claim_date',
            'settlement_value', 'special_health_expenses', 'accident_type',
            'injury_prognosis', 'vehicle_type', 'vehicle_age', 'driver_age',
            'accident_description', 'injury_description', 'exceptional_circumstances',
            'minor_psychological_injury', 'whiplash', 'police_report_filed',
            'special_reduction', 'special_overage', 'general_rest', 'special_additional_injury',
            'special_earnings_loss', 'special_usage_loss', 'special_medications', 'special_asset_damage',
            'special_rehabilitation', 'special_fixes', 'general_fixed', 'general_uplift',
            'special_loaner_vehicle', 'special_trip_costs', 'number_of_passengers'
        ]
        widgets = {
            'accident_date': forms.DateInput(attrs={'type': 'date'}),
            'claim_date': forms.DateInput(attrs={'type': 'date'}),
            'accident_description': forms.Textarea(attrs={'rows': 3}),
            'injury_description': forms.Textarea(attrs={'rows': 3}),
        } 