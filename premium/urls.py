# GovtApplications/urls.py (Officer-specific routes)
from django.urls import path
from . import views

app_name = 'premium'

urlpatterns = [
    path('subscribe/', views.subscribe_premium, name='subscribe'),

]
