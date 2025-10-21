# rainwater_harvesting/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),      # Vendor registration pages
    path('vendor/', include('vendorRegistration.urls')),          # Vendor registration pages
    path('officer/', include('GovtApplications.urls')),          
    path('api/', include('translations.urls')),
    path('calculator/', include('calculator.urls')),              # Calculator pages
    path('api/v1/', include('calculator.api_urls')),              # API endpoints (separate file)
    path('chatbot/', include('chatbot.urls')),                    # Chatbot API
    path('auth/', include('accounts.urls')),                      # Authentication
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
