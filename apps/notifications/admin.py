from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'level', 'read', 'created_at')
    list_filter = ('level', 'read', 'created_at')
    search_fields = ('message',)
    readonly_fields = ('created_at',)
