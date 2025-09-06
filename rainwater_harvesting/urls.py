# rainwater_harvesting/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('calculator.urls')),  # Keep API endpoints
    path('auth/', include('accounts.urls')),      # Put auth under /auth/ prefix
    path('', include('calculator.urls')),         # Calculator handles root URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
