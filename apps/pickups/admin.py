from django.contrib import admin
from .models import Pickup


@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'collector', 'state', 'scheduled_time')
    list_filter = ('state',)
