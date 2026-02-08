from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.SchedulePickupView.as_view(), name='schedule-pickup'),
]
