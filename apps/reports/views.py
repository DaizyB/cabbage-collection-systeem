from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from apps.pickups.models import Pickup


@staff_member_required
def admin_dashboard(request):
    # Basic metrics
    total_pickups = Pickup.objects.count()
    by_state = Pickup.objects.values('state').order_by('state')
    # build chart-friendly data
    state_counts = {s['state']: Pickup.objects.filter(state=s['state']).count() for s in by_state}
    return render(request, 'reports/admin_dashboard.html', {'total_pickups': total_pickups, 'state_counts': state_counts})
