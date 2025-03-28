from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User, Role
from .utils import validate_username, validate_password, validate_full_name, clean_full_name

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=50)
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'role')
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        validate_username(username)
        return username
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        validate_full_name(full_name)
        return clean_full_name(full_name)

class AdminUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=50)
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(name__in=['Admin', 'Finance']),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'role')
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        validate_username(username)
        return username
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        validate_full_name(full_name)
        return clean_full_name(full_name)

class FinanceUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=50)
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(name='Finance'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'role')
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        validate_username(username)
        return username
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        validate_full_name(full_name)
        return clean_full_name(full_name)

class CustomUserChangeForm(UserChangeForm):
    full_name = forms.CharField(max_length=50)
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'role')
        
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        validate_full_name(full_name)
        return clean_full_name(full_name)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'full_name')
        
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        validate_full_name(full_name)
        return clean_full_name(full_name)
        
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if any([current_password, new_password, confirm_password]):
            if not all([current_password, new_password, confirm_password]):
                raise forms.ValidationError("All password fields are required when changing password.")
            
            if not self.instance.check_password(current_password):
                raise forms.ValidationError("Current password is incorrect.")
            
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match.")
            
            validate_password(new_password)
            # Update the instance's password; the view will update the session.
            self.instance.set_password(new_password)
        
        return cleaned_data
