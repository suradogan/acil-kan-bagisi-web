from django import forms
from .models import BloodDonation

class BloodDonationForm(forms.ModelForm):
    class Meta:
        model = BloodDonation
        fields = ['hospital', 'donation_date', 'blood_type', 'amount', 'notes']
        widgets = {
            'donation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 