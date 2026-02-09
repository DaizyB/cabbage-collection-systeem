from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.SchedulePickupView.as_view(), name='schedule-pickup'),
    path('request/', views.request_pickup, name='request-pickup'),
    path('<int:pk>/mark_collected/', views.mark_collected, name='mark-collected'),
    path('<int:pk>/accept/', views.accept_pickup, name='accept-pickup'),
    path('<int:pk>/release/', views.release_pickup, name='release-pickup'),
]
