from django.urls import path
from . import views

urlpatterns = [
    # API endpoints (your existing ones)
    path('calculate/', views.calculate_rainwater_harvest, name='calculate_harvest'),
    path('districts/', views.list_districts, name='list_districts'),
    path('districts/<str:district_name>/', views.get_district_info, name='district_info'),
    
    # Map root and demo to existing listing view (no demo_view in views.py)
    path('', views.demo_view, name='root_districts'),
    path('demo/', views.list_districts, name='demo_page'),

    
]
