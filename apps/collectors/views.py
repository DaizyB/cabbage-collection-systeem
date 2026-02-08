from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    # Minimal collector dashboard: list assigned pickups via relation (implemented in pickups app)
    return render(request, 'collectors/dashboard.html')
