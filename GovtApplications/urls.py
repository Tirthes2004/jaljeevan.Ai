# GovtApplications/urls.py

from django.urls import path
from . import views

app_name = 'officer'

urlpatterns = [
    # Officer routes
    path('login/', views.loginOfficer, name='login'),
    path('logout/', views.logoutOfficer, name='logout'),
    path('register/', views.registerOfficer, name='register'),
    path('', views.application_dashboard, name='officer_dashboard'),
    path('approve/', views.approve_application, name='approve_application'),
    path('reject/', views.reject_application, name='reject_application'),
    path('mark-review/', views.under_review_application, name='under_review_application'),
]
