# calculator/api_urls.py
from django.urls import path
from . import views

app_name = 'calculator_api'

urlpatterns = [
    path('calculate/', views.calculate_rainwater_harvest, name='calculate'),
    path('districts/', views.list_districts, name='districts'),
    path('districts/<str:district_name>/', views.get_district_info, name='district_info'),
    path('chart/<str:district_name>/', views.rainfall_chart, name='rainfall_chart'),  # ✅ This works
    path('chart/line/<str:district_name>/', views.rainfall_line_chart, name='rainfall_line_chart'),  # ✅ ADD THIS LINE
    path('save/', views.save_calculation_manual, name='save_calculation'),
]
