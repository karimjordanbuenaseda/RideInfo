"""
URL configuration for ride_info project.

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
from django.urls import include, path, re_path
from rest_framework import routers

from core.views import *

admin.autodiscover()

router = routers.SimpleRouter()
# Register your viewsets here
router.register(r'rides', RideViewSet, basename='rides')

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r'^api/', include(router.urls)),
]
