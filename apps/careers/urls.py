from django.urls import path
from . import views

urlpatterns = [
    path('become-collector/', views.apply_collector, name='apply-collector'),
    path('become-collector/success/', views.apply_success, name='apply-success'),
    path('application/status/', views.application_status, name='application-status'),
]
