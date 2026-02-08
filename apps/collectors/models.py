from django.db import models
from django.conf import settings


class CollectorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collector_profile')
    bio = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Collector: {self.user.username}"
