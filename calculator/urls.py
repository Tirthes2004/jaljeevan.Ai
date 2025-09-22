# calculator/urls.py
from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.calculator_view, name='calculator'),
    path("rainfall-chart/<str:district_name>/", views.rainfall_chart, name="rainfall-chart"),
    path("rainfall/line/<str:district_name>/", views.rainfall_line_chart, name="rainfall_line_chart"),

]
