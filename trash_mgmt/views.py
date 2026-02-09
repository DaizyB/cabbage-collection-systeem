def contact(request):
    return render(request, 'contact.html')
from django.shortcuts import render


def home(request):
    return render(request, 'index.html')
