from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=32, blank=True)
    backup_contact = models.CharField(max_length=32, blank=True)
    notification_method = models.CharField(max_length=16, choices=[('sms', 'SMS'), ('email', 'Email'), ('inapp', 'In-app')], default='inapp')
    # Preferences
    preferred_days = models.CharField(max_length=64, blank=True)  # e.g. "Mon,Tue,Fri"
    preferred_time = models.CharField(max_length=16, choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')], blank=True)
    trash_types = models.CharField(max_length=64, blank=True)  # e.g. "household,recyclable"
    special_instructions = models.TextField(blank=True)
    # Location
    address_text = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=64, blank=True)
    landmark = models.CharField(max_length=128, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pickup_qr_token = models.CharField(max_length=64, blank=True)
    # System
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user}" 
