
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CropHistory
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class CropRecommendationForm(forms.ModelForm):
    SOIL_TYPES = [
        ('Chalky', 'Chalky'),
        ('Clay', 'Clay'),
        ('Loam', 'Loam'),
        ('Peaty', 'Peaty'),
        ('Sandy', 'Sandy'),
        ('Silty', 'Silty'),
    ]
    soil_type = forms.ChoiceField(choices=SOIL_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CropHistory
        fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'soil_type']
