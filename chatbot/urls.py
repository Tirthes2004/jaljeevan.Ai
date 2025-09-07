# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/', views.chat_api, name='api'),
    path('history/<str:session_id>/', views.chat_history, name='history'),
    # Add more paths as needed
]
