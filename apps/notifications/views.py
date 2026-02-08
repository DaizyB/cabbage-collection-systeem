from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import Notification


def index(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(recipient=request.user)
    else:
        notifs = Notification.objects.filter(recipient__isnull=True)

    return render(request, 'notifications/index.html', {'notifications': notifs})


@require_POST
@login_required
def toggle_read(request, pk):
    try:
        n = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)

    # Only allow recipients to toggle their own notifications
    if n.recipient is None:
        return JsonResponse({'ok': False, 'error': 'Cannot modify public notification'}, status=403)
    if n.recipient != request.user:
        return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)

    n.read = not n.read
    n.save()
    return JsonResponse({'ok': True, 'read': n.read})
