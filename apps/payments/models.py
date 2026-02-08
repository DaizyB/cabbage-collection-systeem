from django.db import models
from django.conf import settings


class Invoice(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_cents = models.IntegerField()
    description = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='transactions')
    provider = models.CharField(max_length=50)
    provider_id = models.CharField(max_length=200, blank=True, null=True)
    succeeded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: wire up webhook endpoints in views
