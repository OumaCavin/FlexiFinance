"""
FlexiFinance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.core import views

# Admin site customization
admin.site.site_header = "FlexiFinance Administration"
admin.site.site_title = "FlexiFinance Admin"
admin.site.index_title = "FlexiFinance Dashboard"

urlpatterns = [
    # Admin interface
    path(settings.ADMIN_URL, admin.site.urls),
    
    # Main website pages
    path('', include('apps.core.urls')),
    
    # API endpoints
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/users/', include('apps.users.api_urls')),
    path('api/v1/loans/', include('apps.loans.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    
    # Web URLs
    path('dashboard/', include('apps.users.web_urls')),
    path('loans/', include('apps.loans.web_urls')),
    path('payments/', include('apps.payments.web_urls')),
    
    # Health check endpoints
    path('health/', include('apps.core.urls')),
    path('api/payments/', include('apps.payments.web_urls')),
    
    # Documentation
    path('docs/', include('docs.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# Custom error handlers
handler404 = views.handler404
handler500 = views.handler500
handler403 = views.handler403
handler400 = views.handler400
