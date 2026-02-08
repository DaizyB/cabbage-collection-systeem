from rest_framework import serializers
from .models import Pickup


class PickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pickup
        fields = ('id', 'address', 'scheduled_time', 'state')
        read_only_fields = ('state',)
