from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from apps.customers.models import Address
from apps.accounts.models_profile import UserProfile
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile, 'addresses': addresses})

@login_required
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Update fields
        profile.phone = request.POST.get('phone', profile.phone)
        profile.backup_contact = request.POST.get('backup_contact', profile.backup_contact)
        profile.notification_method = request.POST.get('notification_method', profile.notification_method)
        profile.preferred_days = request.POST.get('preferred_days', profile.preferred_days)
        profile.preferred_time = request.POST.get('preferred_time', profile.preferred_time)
        profile.trash_types = request.POST.get('trash_types', profile.trash_types)
        profile.special_instructions = request.POST.get('special_instructions', profile.special_instructions)
        profile.address_text = request.POST.get('address_text', profile.address_text)
        profile.region = request.POST.get('region', profile.region)
        profile.landmark = request.POST.get('landmark', profile.landmark)
        try:
            profile.latitude = float(request.POST.get('latitude', profile.latitude or 0))
            profile.longitude = float(request.POST.get('longitude', profile.longitude or 0))
        except Exception:
            pass
        profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')
    addresses = Address.objects.filter(user=request.user)
    return render(
        request,
        'accounts/profile_edit.html',
        {
            'profile': profile,
            'addresses': addresses,
            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        }
    )
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserCreationForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If the client expects JSON return JSON, otherwise redirect
            if _prefers_json(request):
                return JsonResponse({'ok': True, 'id': user.id})
            return redirect('accounts:login')
        if _prefers_json(request):
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
        return render(request, 'accounts/signup.html', {'form': form})
    return render(request, 'accounts/signup.html', {'form': UserCreationForm()})


def login_view(request):
    errors = []
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            errors.append('Username and password are required.')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if _prefers_json(request):
                    return JsonResponse({'ok': True})
                next_url = request.GET.get('next') or reverse('accounts:dashboard')
                return redirect(next_url)
            errors.append('Invalid username or password.')

        # If request expects JSON, return structured error + status
        if _prefers_json(request):
            return JsonResponse({'ok': False, 'errors': errors}, status=401)

    return render(request, 'accounts/login.html', {'errors': errors, 'username': request.POST.get('username', '')})


def _prefers_json(request):
    """Return True when the client likely expects JSON (AJAX/API).

    We check the X-Requested-With header and Accept header.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('Accept', '')
    if 'application/json' in accept:
        return True
    return False


@login_required
def dashboard_dispatch(request):
    user = request.user
    # Approved collector -> collector dashboard
    if getattr(user, 'is_approved_collector', False):
        return collector_dashboard(request)
    # Applicant (has application) but not approved -> redirect to application status page
    if getattr(user, 'has_collector_application', False) and not getattr(user, 'is_approved_collector', False):
        return redirect(reverse('careers:application-status'))
    # Default: general user dashboard
    return user_dashboard(request)


@login_required
def user_dashboard(request):
    from apps.pickups.models import Pickup
    from apps.notifications.models import Notification
    from django.utils import timezone

    user = request.user
    now = timezone.now()
    upcoming = Pickup.objects.filter(customer=user, state=Pickup.STATE_SCHEDULED).order_by('scheduled_time')[:5]
    last = Pickup.objects.filter(customer=user, state=Pickup.STATE_COMPLETED).order_by('-scheduled_time').first()
    history = Pickup.objects.filter(customer=user).order_by('-scheduled_time')[:10]
    notes = Notification.objects.filter(recipient=user)[:10]
    # Get default address (first address), or fallback to profile fields
    default_address = user.addresses.first()
    if not default_address:
        # Fallback: use profile fields as a pseudo-address object
        profile = getattr(user, 'profile', None)
        if profile and profile.address_text:
            class PseudoAddress:
                address_text = profile.address_text
                region = profile.region
                landmark = profile.landmark
            default_address = PseudoAddress()
    context = {
        'upcoming': upcoming,
        'last_pickup': last,
        'history': history,
        'notifications': notes,
        'default_address': default_address,
    }
    return render(request, 'accounts/user_dashboard.html', context)


@login_required
def collector_dashboard(request):
    # Only allow approved collectors here
    if not getattr(request.user, 'is_approved_collector', False):
        return redirect(reverse('careers:become_collector'))
    from apps.pickups.models import Pickup
    from apps.notifications.models import Notification
    from django.utils import timezone

    user = request.user
    today = timezone.localdate()
    # Pickups assigned to this collector
    assigned = Pickup.objects.filter(collector=user, state=Pickup.STATE_ASSIGNED).order_by('scheduled_time')
    # Available pickups (not assigned, scheduled or released)
    available = Pickup.objects.filter(collector__isnull=True, state__in=[Pickup.STATE_SCHEDULED, Pickup.STATE_RELEASED]).order_by('scheduled_time')
    completed_count = Pickup.objects.filter(collector=user, state=Pickup.STATE_COMPLETED).count()
    notes = Notification.objects.filter(recipient=user)[:10]
    context = {
        'assigned': assigned,
        'available': available,
        'completed_count': completed_count,
        'notifications': notes,
    }
    return render(request, 'accounts/collector_dashboard.html', context)

@login_required
def admin_dashboard(request):
    from apps.pickups.models import Pickup
    pickups = Pickup.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_dashboard.html', {'pickups': pickups})
