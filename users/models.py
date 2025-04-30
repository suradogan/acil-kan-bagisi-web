from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    BLOOD_TYPES = [
        ('A+', 'A RhD positive'),
        ('A-', 'A RhD negative'),
        ('B+', 'B RhD positive'),
        ('B-', 'B RhD negative'),
        ('O+', 'O RhD positive'),
        ('O-', 'O RhD negative'),
        ('AB+', 'AB RhD positive'),
        ('AB-', 'AB RhD negative'),
    ]

    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    is_hospital = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return self.username
        
    def can_donate(self):
        """Kullanıcının kan bağışı yapıp yapamayacağını kontrol eder"""
        if not self.last_donation_date:
            return True
        
        # Son bağıştan itibaren 3 ay (90 gün) geçti mi?
        days_since_last_donation = (timezone.now().date() - self.last_donation_date).days
        return days_since_last_donation >= 90
        
    def days_until_next_donation(self):
        """Bir sonraki bağış yapılabilir tarihe kaç gün kaldığını hesaplar"""
        if not self.last_donation_date:
            return 0
            
        days_since_last_donation = (timezone.now().date() - self.last_donation_date).days
        if days_since_last_donation >= 90:
            return 0
        else:
            return 90 - days_since_last_donation
