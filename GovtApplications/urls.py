# pages/urls.py (create this file)
from django.urls import path
from django.urls import include
from . import views


app_name = 'GovtApplications'

urlpatterns = [
    path('', views.application_dashboard, name='application_dashboard'),
    path('form/',views.application_form, name='application_form'),

]