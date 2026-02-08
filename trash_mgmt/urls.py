from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('customers/', include('apps.customers.urls')),
    path('collectors/', include('apps.collectors.urls')),
    path('pickups/', include('apps.pickups.urls')),
    path('payments/', include('apps.payments.urls')),
    path('careers/', include('apps.careers.urls')),
    path('quizzes/', include('apps.quizzes.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('reports/', include('apps.reports.urls')),
]
