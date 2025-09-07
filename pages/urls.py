# pages/urls.py (create this file)
from django.urls import path
from django.urls import include
from . import views


app_name = 'pages'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('calculator/', include('calculator.urls')),
    # path('features/', views.about_view, name='features'),  # Same as about
    # path('technology/', views.technology_view, name='technology'),
    # path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
