from django.contrib import admin
from .models import CollectorApplication


@admin.register(CollectorApplication)
class CollectorApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'status', 'test_score', 'applied_at')
    list_filter = ('status', 'test_passed')
    readonly_fields = ('applied_at', 'test_score')
    search_fields = ('full_name', 'email', 'phone', 'national_id')
    fieldsets = (
        ('Personal', {'fields': ('full_name', 'phone', 'email', 'national_id')}),
        ('Driving & Vehicle', {'fields': ('driving_license_number', 'license_class', 'license_expiry', 'vehicle_number_plate', 'vehicle_type')}),
        ('Uploads', {'fields': ('resume', 'id_photo', 'license_photo', 'plate_photo', 'selfie_photo')}),
        ('Test & Status', {'fields': ('answers', 'test_score', 'test_passed', 'status', 'reviewed')}),
    )
    actions = ['approve_collector', 'reject_application']

    def approve_collector(self, request, queryset):
        queryset.update(status=CollectorApplication.STATUS_APPROVED)

    def reject_application(self, request, queryset):
        queryset.update(status=CollectorApplication.STATUS_REJECTED)

    approve_collector.short_description = 'Mark selected as Approved'
    reject_application.short_description = 'Mark selected as Rejected'
