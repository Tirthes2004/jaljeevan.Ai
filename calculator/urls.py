# calculator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main page - your demo.html with auth modals
    path('', views.demo_view, name='home'),  # Root URL shows demo.html
    path('demo/', views.demo_view, name='demo'),  # Also accessible via /demo/
    
    # API endpoints
    path('calculate/', views.calculate_rainwater_harvest, name='calculate_harvest'),
    path('districts/', views.list_districts, name='list_districts'),
    path('districts/<str:district_name>/', views.get_district_info, name='district_info'),
]
