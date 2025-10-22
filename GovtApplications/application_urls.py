# GovtApplications/application_urls.py (Public application routes)
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Application form at /applications/form/
    path('form/', views.application_form, name='form'),
    
    # Submit application API at /applications/api/submit/
    path('api/submit/', views.submit_application, name='submit'),

    # Track applications at /applications/track/
    path('track/', views.track_applications, name='track_applications'),



]
