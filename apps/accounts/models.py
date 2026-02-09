from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('collector', 'Collector'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    collector_approved = models.BooleanField(default=False)

    @property
    def is_collector(self):
        return self.role == 'collector'

    @property
    def has_collector_application(self):
        # lazy import to avoid circular imports
        from django.apps import apps
        CollectorApplication = apps.get_model('careers', 'CollectorApplication')
        if CollectorApplication is None:
            return False
        # check by linked user first, then by email
        if CollectorApplication.objects.filter(user=self).exists():
            return True
        if self.email:
            return CollectorApplication.objects.filter(email__iexact=self.email).exists()
        return False

    @property
    def is_approved_collector(self):
        return self.is_collector and bool(self.collector_approved)
