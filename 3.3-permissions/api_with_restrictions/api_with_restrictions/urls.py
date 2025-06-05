# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from advertisements.views import AdvertisementViewSet 

router = DefaultRouter()
router.register(r'advertisements', AdvertisementViewSet) 


urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]