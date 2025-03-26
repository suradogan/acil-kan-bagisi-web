from rest_framework import serializers
from .models import BloodDonation
from users.serializers import UserSerializer
from hospitals.serializers import HospitalSerializer

class BloodDonationSerializer(serializers.ModelSerializer):
    donor_details = UserSerializer(source='donor', read_only=True)
    hospital_details = HospitalSerializer(source='hospital', read_only=True)
    
    class Meta:
        model = BloodDonation
        fields = '__all__' 