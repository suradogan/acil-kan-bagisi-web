from django.db import models
from users.models import User
from hospitals.models import Hospital
from django.utils import timezone

class BloodDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateTimeField()
    blood_type = models.CharField(max_length=3)
    amount = models.IntegerField(help_text="Amount in milliliters")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_emergency = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.donor.username} - {self.blood_type} - {self.donation_date}"
        
    class Meta:
        ordering = ['-donation_date']

class EmergencyBloodRequest(models.Model):
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('fulfilled', 'Karşılandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_requests')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='emergency_requests')
    blood_type = models.CharField(max_length=3)
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    urgency_level = models.IntegerField(default=1, help_text="1: Normal, 2: Acil, 3: Çok Acil")
    units_needed = models.IntegerField(default=1)
    units_received = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.patient_name} - {self.blood_type} - {self.created_at}"
        
    def is_expired(self):
        return timezone.now() > self.expires_at
        
    def is_fulfilled(self):
        return self.units_received >= self.units_needed
        
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Varsayılan olarak 24 saat geçerli
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
            
        # İhtiyaç karşılandıysa durumu otomatik güncelle
        if self.is_fulfilled() and self.status == 'active':
            self.status = 'fulfilled'
            
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-created_at', '-urgency_level']

class BloodDonationResponse(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
        ('completed', 'Tamamlandı'),
    ]
    
    emergency_request = models.ForeignKey(EmergencyBloodRequest, on_delete=models.CASCADE, related_name='responses')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_responses')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    arrival_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.donor.username} - {self.emergency_request.blood_type} - {self.status}"
        
    class Meta:
        ordering = ['-created_at']
        unique_together = ['emergency_request', 'donor']
