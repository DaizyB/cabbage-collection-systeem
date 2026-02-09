from django.db import models
from django.conf import settings


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    address_text = models.TextField()
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_place_id = models.CharField(max_length=128, blank=True)
    region = models.CharField(max_length=64, blank=True)
    landmark = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # TODO: hook geocoding service here. Keep client-side keyless Google Maps skeleton in templates.
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_text} ({self.user})"
