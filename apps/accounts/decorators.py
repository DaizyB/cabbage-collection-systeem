from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def approved_collector_required(view_func):
    """Decorator that allows only approved collectors.

    - If not authenticated -> redirect to login
    - If has application but not approved -> redirect to application status page
    - If never applied -> redirect to apply page
    - If approved -> allow
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            login_url = reverse('login') if 'login' else '/accounts/login/'
            return redirect(f"{login_url}?next={request.path}")
        if getattr(user, 'is_approved_collector', False):
            return view_func(request, *args, **kwargs)
        # Applicant but not approved
        if getattr(user, 'has_collector_application', False):
            return redirect(reverse('careers:application-status'))
        # Not applied
        return redirect(reverse('careers:apply-collector'))

    return _wrapped
