"""
URL configuration for record_recogniser project.

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
from django.urls import path
from detection.views import detect_object, detect, home, add_to_collection, catalogue
from django.conf import settings
from django.conf.urls.static import static

app_name = 'detection'

#Define URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
path('', home, name='default_home'),
    path('home/', home, name='home'),
    path('detect/', detect, name='detect'),
    path('detect/recognition/', detect_object, name='detect_object'),
    path('catalogue/', catalogue, name='catalogue'),
    path('add_to_collection/', add_to_collection, name='add_to_collection'),
]

#Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)