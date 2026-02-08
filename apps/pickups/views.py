from rest_framework import generics, permissions
from .models import Pickup
from .serializers import PickupSerializer


class SchedulePickupView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PickupSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
