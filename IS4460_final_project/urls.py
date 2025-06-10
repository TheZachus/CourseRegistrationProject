"""
URL configuration for IS4460_final_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Change the Django admin URL prefix because we use django_admin
admin.site.site_url = None  # Remove the "View site" link
admin.site.site_header = 'Course Registration System Admin'
admin.site.site_title = 'Course Registration Admin'
admin.site.index_title = 'System Administration'

urlpatterns = [
    # Use django_admin as the path for the Django admin
    path('django_admin/', admin.site.urls),
    
    # Include your course_registration URLs which have your custom admin/ paths
    path('', include('course_registration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)