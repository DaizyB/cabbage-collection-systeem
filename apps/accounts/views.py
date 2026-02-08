from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserCreationForm
from django.http import JsonResponse


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If the client expects JSON return JSON, otherwise redirect
            if _prefers_json(request):
                return JsonResponse({'ok': True, 'id': user.id})
            return redirect('home')
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
                next_url = request.GET.get('next') or 'home'
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
