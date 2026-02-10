from datetime import timedelta
from apps.accounts.decorators import approved_collector_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

@approved_collector_required
@login_required
def accept_pickup(request, pk):
    with transaction.atomic():
        updated = (
            Pickup.objects
            .select_for_update()
            .filter(pk=pk, collector__isnull=True, state__in=[Pickup.STATE_SCHEDULED, Pickup.STATE_RELEASED])
            .update(collector=request.user, state=Pickup.STATE_ASSIGNED)
        )
        if updated != 1:
            messages.error(request, 'Pickup already assigned.')
            return redirect('accounts:collector_dashboard')
    messages.success(request, 'Pickup accepted.')
    return redirect('accounts:collector_dashboard')

@approved_collector_required
@login_required
def release_pickup(request, pk):
    p = get_object_or_404(Pickup, pk=pk)
    if p.collector != request.user:
        messages.error(request, 'You are not assigned to this pickup.')
        return redirect('accounts:collector_dashboard')
    # Enforce minimum 3 days before scheduled_time
    from django.utils import timezone
    if (p.scheduled_time - timezone.now()) < timedelta(days=3):
        messages.error(request, 'Cannot release pickup less than 3 days before scheduled time.')
        return redirect('accounts:collector_dashboard')
    reason = request.POST.get('reason', '')
    p.release(reason)
    messages.success(request, 'Pickup released for other collectors.')
    return redirect('accounts:collector_dashboard')
from rest_framework import generics, permissions
from .models import Pickup
from .serializers import PickupSerializer
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import approved_collector_required


class SchedulePickupView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PickupSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


@login_required
def request_pickup(request):
    if request.method != 'POST':
        return redirect('/')
    # Minimal handling: create a Pickup scheduled for the chosen date at noon
    from django.utils import timezone
    from datetime import datetime
    import secrets
    from apps.accounts.models_profile import UserProfile
    trash_type = request.POST.get('trash_type', 'household')
    preferred_date = request.POST.get('preferred_date')
    notes = request.POST.get('notes', '')
    # Find a default address for user (first address). If none, create from profile.
    addr = None
    try:
        addr = request.user.addresses.first()
    except Exception:
        addr = None
    if not addr:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.address_text and profile.latitude is not None and profile.longitude is not None:
            from apps.customers.models import Address
            addr = Address.objects.create(
                user=request.user,
                address_text=profile.address_text,
                region=profile.region,
                landmark=profile.landmark,
                lat=profile.latitude,
                lng=profile.longitude,
            )
    if not addr:
        # Only show error if not in admin
        if not request.path.startswith('/admin/'):
            messages.error(request, 'Please set a default pickup address in your profile before requesting a pickup.')
        return redirect('accounts:dashboard')
    # parse date
    if not preferred_date:
        messages.error(request, 'Please select a preferred date for your pickup request.')
        return redirect('accounts:dashboard')
    try:
        scheduled = datetime.fromisoformat(preferred_date)
    except Exception:
        messages.error(request, 'Invalid date format. Please select a valid date for your pickup request.')
        return redirect('accounts:dashboard')
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.pickup_qr_token:
        profile.pickup_qr_token = secrets.token_urlsafe(16)
        profile.save(update_fields=['pickup_qr_token'])
    p = Pickup.objects.create(
        customer=request.user,
        address=addr,
        scheduled_time=scheduled,
        trash_type=trash_type,
        verification_token=profile.pickup_qr_token,
    )
    messages.success(request, 'Pickup requested successfully.')
    return redirect('accounts:dashboard')


@require_POST
@approved_collector_required
def mark_collected(request, pk):
    p = get_object_or_404(Pickup, pk=pk)
    # Only assigned collector may mark collected
    if p.collector != request.user:
        return redirect('accounts:dashboard')
    if p.state != Pickup.STATE_ASSIGNED:
        messages.error(request, 'Pickup is not assigned.')
        return redirect('accounts:collector_dashboard')
    code = request.POST.get('verification_code', '').strip()
    if not code or not p.verification_token:
        messages.error(request, 'Verification code is required.')
        return redirect('accounts:collector_dashboard')
    if code != p.verification_token:
        messages.error(request, 'Verification failed. QR code does not match this pickup.')
        return redirect('accounts:collector_dashboard')
    from django.utils import timezone
    p.state = Pickup.STATE_COMPLETED
    p.verified_at = timezone.now()
    p.save(update_fields=['state', 'verified_at'])
    messages.success(request, 'Pickup verified and marked as collected.')
    return redirect('accounts:collector_dashboard')
