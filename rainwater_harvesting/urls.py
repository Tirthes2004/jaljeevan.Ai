# rainwater_harvesting/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),  # Home and static pages
    path('vendor/', include('vendorRegistration.urls')),  # Vendor registration
    path('officer/', include('GovtApplications.urls')),  # Officer dashboard & management
    path('applications/', include('GovtApplications.application_urls')),  # Public application forms
    path('api/', include('translations.urls')),  # Translation API
    path('calculator/', include('calculator.urls')),  # Calculator pages
    path('api/v1/', include('calculator.api_urls')),  # Calculator API endpoints
    path('chatbot/', include('chatbot.urls')),  # Chatbot API
    path('auth/', include('accounts.urls')),  # Authentication
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('images/favicon.ico')
    )),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
