from django.contrib import admin
from .models import CollectorProfile


@admin.register(CollectorProfile)
class CollectorAdmin(admin.ModelAdmin):
    list_display = ('user', 'active')
