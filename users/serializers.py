from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from donations.models import BloodDonation

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 
                  'confirm_password', 'blood_type', 'phone', 'city', 'district', 
                  'address', 'latitude', 'longitude', 'last_donation_date', 
                  'is_hospital', 'is_available', 'notification_enabled')
        read_only_fields = ('id',)
        
    def validate(self, data):
        # Şifre oluşturma veya değiştirme durumunda doğrulama yap
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Şifreler eşleşmiyor."})
            
            # Şifre doğrulama
            validate_password(data['password'])
            
        return data
    
    def create(self, validated_data):
        # Şifre doğrulama alanını temizle
        validated_data.pop('confirm_password', None)
        
        # Kullanıcı oluştur
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        # Şifre doğrulama alanını temizle
        validated_data.pop('confirm_password', None)
        
        # Şifre değiştirildi mi kontrol et
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Diğer alanları güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    can_donate = serializers.BooleanField(read_only=True)
    days_until_next_donation = serializers.IntegerField(read_only=True)
    donation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'blood_type', 'phone', 'city', 'district', 'address',
                  'latitude', 'longitude', 'last_donation_date', 
                  'can_donate', 'days_until_next_donation', 'donation_count',
                  'is_available', 'notification_enabled')
        read_only_fields = ('id', 'username', 'email')
    
    def get_donation_count(self, obj):
        return BloodDonation.objects.filter(donor=obj).count() 