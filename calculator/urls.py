# calculator/urls.py
from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    # ✅ Calculator page routes
    path('', views.calculator_view, name='calculator'),  # /calculator/ -> calculator page
    
    # ✅ API routes (keep existing)
    path('calculate/', views.calculate_rainwater_harvest, name='calculate'),
    path('districts/', views.list_districts, name='districts'),
    path('districts/<str:district_name>/', views.get_district_info, name='district_info'),
]
