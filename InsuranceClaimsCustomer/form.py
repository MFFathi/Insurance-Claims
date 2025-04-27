from django import forms
from .model import ClaimEntry

class ClaimEntryForm(forms.ModelForm):
    class Meta:
        model = ClaimEntry
        fields = ['accident_type', 'injury_prognosis', 'expense']
