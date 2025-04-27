from django import forms
from .models import MLModel

class MLModelForm(forms.ModelForm):
    class Meta:
        model = MLModel
        fields = ['name', 'description', 'model_file', 'version', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_model_file(self):
        model_file = self.cleaned_data.get('model_file')
        if model_file:
            # Check file extension
            ext = model_file.name.split('.')[-1].lower()
            if ext not in ['pkl', 'joblib', 'h5', 'keras']:
                raise forms.ValidationError("Only .pkl, .joblib, .h5, and .keras files are allowed.")
            # Check file size (max 100MB)
            if model_file.size > 100 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 100MB.")
        return model_file 