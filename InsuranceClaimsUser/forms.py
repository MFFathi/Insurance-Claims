from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User, Role
from .utils import validate_username, validate_password, validate_full_name, clean_full_name

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=50)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    
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
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    
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