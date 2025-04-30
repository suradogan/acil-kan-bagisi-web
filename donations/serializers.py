from rest_framework import serializers
from .models import BloodDonation, EmergencyBloodRequest, BloodDonationResponse
from users.serializers import UserSerializer
from hospitals.serializers import HospitalSerializer

class BloodDonationSerializer(serializers.ModelSerializer):
    donor_details = UserSerializer(source='donor', read_only=True)
    hospital_details = HospitalSerializer(source='hospital', read_only=True)
    
    class Meta:
        model = BloodDonation
        fields = ('id', 'donor', 'donor_details', 'hospital', 'hospital_details',
                  'donation_date', 'blood_type', 'amount', 'notes', 'created_at', 
                  'status', 'is_emergency')
        read_only_fields = ('id', 'created_at')

class EmergencyBloodRequestSerializer(serializers.ModelSerializer):
    requester_details = UserSerializer(source='requester', read_only=True)
    hospital_details = HospitalSerializer(source='hospital', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_fulfilled = serializers.BooleanField(read_only=True)
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = EmergencyBloodRequest
        fields = ('id', 'requester', 'requester_details', 'hospital', 'hospital_details',
                 'blood_type', 'patient_name', 'patient_phone', 'description',
                 'created_at', 'expires_at', 'status', 'urgency_level', 
                 'units_needed', 'units_received', 'is_expired', 'is_fulfilled',
                 'remaining_time')
        read_only_fields = ('id', 'created_at', 'is_expired', 'is_fulfilled')
    
    def get_remaining_time(self, obj):
        from django.utils import timezone
        if obj.expires_at > timezone.now():
            time_diff = obj.expires_at - timezone.now()
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "0h 0m"

class BloodDonationResponseSerializer(serializers.ModelSerializer):
    donor_details = UserSerializer(source='donor', read_only=True)
    emergency_request_details = EmergencyBloodRequestSerializer(source='emergency_request', read_only=True)
    
    class Meta:
        model = BloodDonationResponse
        fields = ('id', 'emergency_request', 'emergency_request_details', 'donor',
                 'donor_details', 'created_at', 'status', 'arrival_time', 'notes')
        read_only_fields = ('id', 'created_at') 