from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bus_stations.urls')),  # Включаем urls.py из приложения bus_stations
]