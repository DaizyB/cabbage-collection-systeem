from django.db import models
from django.conf import settings
import secrets


class Pickup(models.Model):
    TRASH_TYPE_HOUSEHOLD = 'household'
    TRASH_TYPE_RECYCLABLE = 'recyclable'
    TRASH_TYPE_BULK = 'bulk'
    TRASH_TYPE_CHOICES = [
        (TRASH_TYPE_HOUSEHOLD, 'Household'),
        (TRASH_TYPE_RECYCLABLE, 'Recyclable'),
        (TRASH_TYPE_BULK, 'Bulk'),
    ]
    trash_type = models.CharField(max_length=20, choices=TRASH_TYPE_CHOICES, default=TRASH_TYPE_HOUSEHOLD)

    STATE_SCHEDULED = 'scheduled'
    STATE_ASSIGNED = 'assigned'
    STATE_IN_PROGRESS = 'in_progress'
    STATE_COMPLETED = 'completed'
    STATE_RELEASED = 'released'
    STATE_FAILED = 'failed'
    STATE_CHOICES = [
        (STATE_SCHEDULED, 'Scheduled'),
        (STATE_ASSIGNED, 'Assigned'),
        (STATE_IN_PROGRESS, 'In Progress'),
        (STATE_COMPLETED, 'Completed'),
        (STATE_RELEASED, 'Released'),
        (STATE_FAILED, 'Failed'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pickups')
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_pickups')
    release_reason = models.TextField(null=True, blank=True)
    address = models.ForeignKey('customers.Address', on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)
    proof_photo = models.ImageField(upload_to='proofs/', null=True, blank=True)
    verification_token = models.CharField(max_length=64, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.verification_token and self.customer_id:
            profile = getattr(self.customer, 'profile', None)
            if profile:
                if not profile.pickup_qr_token:
                    profile.pickup_qr_token = secrets.token_urlsafe(16)
                    profile.save(update_fields=['pickup_qr_token'])
                self.verification_token = profile.pickup_qr_token
        super().save(*args, **kwargs)

    def assign(self, collector):
        self.collector = collector
        self.state = self.STATE_ASSIGNED
        self.save()

    def start(self):
        self.state = self.STATE_IN_PROGRESS
        self.save()

    def complete(self):
        self.state = self.STATE_COMPLETED
        self.save()

    def release(self, reason):
        self.state = self.STATE_RELEASED
        self.release_reason = reason
        self.collector = None
        self.save()

    def fail(self, reason=None):
        self.state = self.STATE_FAILED
        self.release_reason = reason
        self.save()

    def __str__(self):
        return f"Pickup {self.id} for {self.customer} at {self.scheduled_time}"
