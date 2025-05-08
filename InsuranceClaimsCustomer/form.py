from django import forms
from .models import ClaimEntry

class ClaimEntryForm(forms.ModelForm):
    class Meta:
        model = ClaimEntry
        fields = ['accident_type', 'injury_prognosis', 'expense']
