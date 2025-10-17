# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'vendorRegistration'

urlpatterns = [
    path('', views.vendorRegistration, name='vendorRegistration'),
    path('submit/', views.vendor_register, name='vendor_register'),
]
