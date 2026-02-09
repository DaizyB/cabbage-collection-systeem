from datetime import timedelta
from apps.accounts.decorators import approved_collector_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@approved_collector_required
@login_required
def accept_pickup(request, pk):
    p = get_object_or_404(Pickup, pk=pk)
    if p.collector or p.state not in [Pickup.STATE_SCHEDULED, Pickup.STATE_RELEASED]:
        messages.error(request, 'Pickup already assigned.')
        return redirect('accounts:collector_dashboard')
    p.assign(request.user)
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
    trash_type = request.POST.get('trash_type', 'household')
    preferred_date = request.POST.get('preferred_date')
    notes = request.POST.get('notes', '')
    # Find a default address for user (first address) - best-effort
    try:
        addr = request.user.addresses.first()
    except Exception:
        addr = None
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
    p = Pickup.objects.create(customer=request.user, address=addr, scheduled_time=scheduled, trash_type=trash_type)
    messages.success(request, 'Pickup requested successfully.')
    return redirect('accounts:dashboard')


@require_POST
@approved_collector_required
def mark_collected(request, pk):
    p = get_object_or_404(Pickup, pk=pk)
    # Only assigned collector may mark collected
    if p.collector != request.user:
        return redirect('accounts:dashboard')
    p.complete()
    messages.success(request, 'Marked as collected.')
    return redirect('accounts:dashboard')
