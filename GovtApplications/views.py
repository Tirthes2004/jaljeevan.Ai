from django.shortcuts import render

# Create your views here.

def application_form(request):
    return render(request, 'application_form.html')


def application_dashboard(request):
    return render(request, 'application_dashboard.html')