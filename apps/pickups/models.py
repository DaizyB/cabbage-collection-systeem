from django.db import models
from django.conf import settings


class Pickup(models.Model):
    STATE_SCHEDULED = 'scheduled'
    STATE_IN_PROGRESS = 'in_progress'
    STATE_COMPLETED = 'completed'
    STATE_FAILED = 'failed'

    STATE_CHOICES = [
        (STATE_SCHEDULED, 'Scheduled'),
        (STATE_IN_PROGRESS, 'In Progress'),
        (STATE_COMPLETED, 'Completed'),
        (STATE_FAILED, 'Failed'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pickups')
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_pickups')
    address = models.ForeignKey('customers.Address', on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)
    proof_photo = models.ImageField(upload_to='proofs/', null=True, blank=True)

    def start(self, collector):
        self.collector = collector
        self.state = self.STATE_IN_PROGRESS
        self.save()

    def complete(self):
        self.state = self.STATE_COMPLETED
        self.save()

    def fail(self, reason=None):
        self.state = self.STATE_FAILED
        # TODO: store failure reason in a field
        self.save()

    def __str__(self):
        return f"Pickup {self.id} for {self.customer} at {self.scheduled_time}"
