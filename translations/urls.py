from django.urls import path
from . import views

urlpatterns = [
    path('translate/batch/', views.translate_batch, name='translate_batch'),
]
