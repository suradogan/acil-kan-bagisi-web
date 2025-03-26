from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'blood_type', 
                  'phone', 'city', 'district', 'is_hospital')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['blood_type'].required = True
        self.fields['phone'].required = True
        self.fields['city'].required = True
        self.fields['district'].required = True

class CustomUserChangeForm(UserChangeForm):
    password = None  # Remove password field from the form
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'blood_type', 
                  'phone', 'city', 'district', 'last_donation_date')
        widgets = {
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
        } 