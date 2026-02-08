from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook(request):
    # TODO: validate signature from payment provider and process event
    # This is a skeleton endpoint for providers like Stripe/PayPal.
    return JsonResponse({'ok': True})
