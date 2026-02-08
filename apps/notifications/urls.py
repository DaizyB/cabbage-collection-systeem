from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='notifications-index'),
    path('toggle/<int:pk>/', views.toggle_read, name='notifications-toggle'),
]
