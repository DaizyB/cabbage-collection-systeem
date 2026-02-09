from django.contrib import admin
from .models import CollectorApplication
from django.utils import timezone


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

    def set_kyc_under_verification(self, request, queryset):
        from apps.notifications.models import Notification
        for app in queryset:
            app.status = CollectorApplication.KYC_UNDER_VERIFICATION
            app.status_changed_at = timezone.now()
            app.reviewed = True
            app.save()
            if app.user:
                Notification.objects.create(recipient=app.user, message='Your KYC documents are being verified.', level='info')

    def set_kyc_failed(self, request, queryset):
        from apps.notifications.models import Notification
        for app in queryset:
            app.status = CollectorApplication.KYC_VERIFICATION_FAILED
            app.status_changed_at = timezone.now()
            app.reviewed = True
            app.save()
            if app.user:
                Notification.objects.create(recipient=app.user, message='KYC verification failed. Please contact administrator.', level='danger')

    set_kyc_under_verification.short_description = 'Mark selected as KYC: under verification'
    set_kyc_failed.short_description = 'Mark selected as KYC: failed'
    actions += ['set_kyc_under_verification', 'set_kyc_failed']

    def approve_collector(self, request, queryset):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for app in queryset:
            # find or create a user for this application by email
            user = None
            if app.user:
                user = app.user
            else:
                user = User.objects.filter(email__iexact=app.email).first()
            if not user:
                # create a minimal user; admin should reset password or notify
                username_base = (app.email.split('@')[0] if app.email else app.full_name.replace(' ', '').lower())
                username = username_base
                i = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{i}"
                    i += 1
                user = User.objects.create(username=username, email=app.email, first_name=app.full_name)
                user.set_unusable_password()
                user.save()
            # promote to collector role and mark approved
            user.role = 'collector'
            user.collector_approved = True
            user.save()
            # link application and mark approved
            app.user = user
            app.status = CollectorApplication.APPLICATION_APPROVED
            app.reviewed = True
            app.status_changed_at = timezone.now()
            app.save()

    def reject_application(self, request, queryset):
        queryset.update(status=CollectorApplication.STATUS_REJECTED)

    approve_collector.short_description = 'Mark selected as Approved'
    reject_application.short_description = 'Mark selected as Rejected'
