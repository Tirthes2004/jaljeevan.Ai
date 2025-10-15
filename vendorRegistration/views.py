from django.shortcuts import render

# Create your views here.

def vendorRegistration(request):
    return render(request, 'vendorRegistration.html')