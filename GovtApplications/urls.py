# GovtApplications/urls.py (Officer-specific routes)
from django.urls import path
from . import views

app_name = 'officer'

urlpatterns = [
    # Officer dashboard at /officer/
    path('', views.application_dashboard, name='dashboard'),

    # Officer registration at /officer/register/
    path('register/', views.registerOfficer, name='register'),
    
    # Officer login at /officer/login/
    path('login/', views.loginOfficer, name='login'),
    
    # Officer logout at /officer/logout/
    path('logout/', views.logoutOfficer, name='logout'),

    # Officers - Approve/Reject applications
    path('approve/', views.approve_application, name='approve'),
    path('reject/', views.reject_application, name='reject'),
    path('under-review/', views.under_review_application, name='under_review'),

]
