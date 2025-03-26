from django.contrib.auth.models import AbstractUser
from django.db import models

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
    last_donation_date = models.DateField(null=True, blank=True)
    is_hospital = models.BooleanField(default=False)

    def __str__(self):
        return self.username
