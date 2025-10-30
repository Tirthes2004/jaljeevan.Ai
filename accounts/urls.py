# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Remove the conflicting demo view
    path('register/', views.registerUser, name='registerUser'),  # Changed to register/
    path('login/', views.loginUser, name='loginUser'),           # Changed to login/
    path('logout/', views.logoutUser, name='logoutUser'),        # Changed to logout/
    path('profile/', views.profileView, name='profileView'),     # New profile view
]
