# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Landing page
    path('', include('landing.urls')),
    
    # Surveys
    path('survey/', include('surveys.urls')),
    
    # Admin panel
    path('admin-panel/', include('admin_panel.urls')),
    
    # Reports (NEW)
    path('reports/', include('reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)