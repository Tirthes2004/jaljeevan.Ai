# rainwater_harvesting/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ Main pages at root level
    path('', include('pages.urls')),                # Home and static pages
    
    # ✅ Calculator under /calculator/
    path('calculator/', include('calculator.urls')), # Calculator pages
    
    # ✅ API endpoints
    path('api/v1/', include('calculator.urls')),     # Keep API endpoints
    
    # ✅ Authentication
    path('auth/', include('accounts.urls')),         # Auth under /auth/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
