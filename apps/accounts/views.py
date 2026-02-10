from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.accounts.models_profile import UserProfile
from apps.customers.models import Address
from .forms import UserCreationForm


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
        lat_raw = request.POST.get('latitude', '')
        lng_raw = request.POST.get('longitude', '')
        try:
            profile.latitude = float(lat_raw) if lat_raw != '' else None
            profile.longitude = float(lng_raw) if lng_raw != '' else None
        except Exception:
            profile.latitude = None
            profile.longitude = None

        missing_location = (
            not profile.address_text
            or not profile.region
            or profile.latitude is None
            or profile.longitude is None
        )
        if missing_location:
            messages.error(request, 'Please provide a complete pickup location (address, region, latitude, longitude).')
        else:
            profile.save()
            addr = Address.objects.filter(user=request.user).first()
            if addr:
                addr.address_text = profile.address_text
                addr.region = profile.region
                addr.landmark = profile.landmark
                addr.lat = profile.latitude
                addr.lng = profile.longitude
                addr.save()
            else:
                Address.objects.create(
                    user=request.user,
                    address_text=profile.address_text,
                    region=profile.region,
                    landmark=profile.landmark,
                    lat=profile.latitude,
                    lng=profile.longitude,
                )
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
    import secrets
    from apps.accounts.models_profile import UserProfile

    user = request.user
    now = timezone.now()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if not profile.pickup_qr_token:
        profile.pickup_qr_token = secrets.token_urlsafe(16)
        profile.save(update_fields=['pickup_qr_token'])
    upcoming = Pickup.objects.filter(customer=user, state=Pickup.STATE_SCHEDULED).order_by('scheduled_time')[:5]
    last = Pickup.objects.filter(customer=user, state=Pickup.STATE_COMPLETED).order_by('-scheduled_time').first()
    history = Pickup.objects.filter(customer=user).order_by('-scheduled_time')[:10]
    notes = Notification.objects.filter(recipient=user)[:10]
    # Use profile location to decide if pickup can be requested
    default_address = None
    profile = getattr(user, 'profile', None)
    if profile and profile.address_text and profile.latitude is not None and profile.longitude is not None:
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
        'pickup_qr_token': profile.pickup_qr_token,
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
    todays_assignments = assigned.filter(scheduled_time__date=today)
    from django.utils import timezone
    completed = Pickup.objects.filter(
        collector=user,
        state=Pickup.STATE_COMPLETED,
        scheduled_time__gte=timezone.now() - timezone.timedelta(days=30),
    ).order_by('-scheduled_time')[:5]
    # Available pickups (not assigned, scheduled or released)
    available = Pickup.objects.filter(collector__isnull=True, state__in=[Pickup.STATE_SCHEDULED, Pickup.STATE_RELEASED]).order_by('scheduled_time')
    completed_count = Pickup.objects.filter(collector=user, state=Pickup.STATE_COMPLETED).count()
    notes = Notification.objects.filter(recipient=user)[:10]
    context = {
        'assigned': assigned,
        'todays_assignments': todays_assignments,
        'available': available,
        'completed_count': completed_count,
        'completed': completed,
        'notifications': notes,
    }
    return render(request, 'accounts/collector_dashboard.html', context)


@login_required
def collector_history(request):
    from apps.pickups.models import Pickup
    from django.utils import timezone
    user = request.user
    # Only allow approved collectors
    if not getattr(user, 'is_approved_collector', False):
        return redirect(reverse('careers:become_collector'))
    completed = Pickup.objects.filter(
        collector=user,
        state=Pickup.STATE_COMPLETED,
        scheduled_time__gte=timezone.now() - timezone.timedelta(days=30),
    ).order_by('-scheduled_time')
    return render(request, 'accounts/collector_history.html', {'completed': completed})

@login_required
def admin_dashboard(request):
    from apps.pickups.models import Pickup
    pickups = Pickup.objects.all().order_by('-created_at')
    pickup_requests = Pickup.objects.filter(state__in=[Pickup.STATE_SCHEDULED, Pickup.STATE_RELEASED]).order_by('-created_at')
    return render(
        request,
        'accounts/admin_dashboard.html',
        {
            'pickups': pickups,
            'pickup_requests': pickup_requests,
        },
    )
