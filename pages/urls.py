# pages/urls.py (create this file)
from django.urls import path
from django.urls import include
from . import views


app_name = 'pages'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('contact/', views.contact_view, name='contact'),
    path('calculator/', include('calculator.urls')),
    path('vendor_section/', views.vendor_view, name='vendor_section'),
    path('applications/', include('GovtApplications.urls')),
    # path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
