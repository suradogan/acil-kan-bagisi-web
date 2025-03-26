from django.db import models
from users.models import User
from hospitals.models import Hospital

class BloodDonation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateTimeField()
    blood_type = models.CharField(max_length=3)
    amount = models.IntegerField(help_text="Amount in milliliters")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.donor.username} - {self.blood_type} - {self.donation_date}"
