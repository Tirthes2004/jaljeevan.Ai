# GovtApplications/application_urls.py

from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Public application routes
    path('form/', views.application_form, name='form'),
    path('api/submit/', views.submit_application, name='submit_application'),
    path('track/', views.track_applications, name='track_applications'),
]
