from django import forms
from .models import BloodDonation, EmergencyBloodRequest
from hospitals.models import Hospital

class BloodDonationForm(forms.ModelForm):
    class Meta:
        model = BloodDonation
        fields = ['hospital', 'donation_date', 'amount', 'notes']
        widgets = {
            'donation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class EmergencyBloodRequestForm(forms.ModelForm):
    URGENCY_CHOICES = [
        (1, 'Normal'),
        (2, 'Acil'),
        (3, 'Çok Acil'),
    ]
    
    urgency_level = forms.ChoiceField(
        choices=URGENCY_CHOICES,
        widget=forms.RadioSelect,
        initial=1
    )
    
    class Meta:
        model = EmergencyBloodRequest
        fields = [
            'hospital', 'blood_type', 'patient_name', 'patient_phone', 
            'description', 'urgency_level', 'units_needed'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'patient_name': forms.TextInput(attrs={'placeholder': 'Hasta adı'}),
            'patient_phone': forms.TextInput(attrs={'placeholder': 'İletişim telefonu (opsiyonel)'}),
        } 