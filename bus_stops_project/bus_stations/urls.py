from django.urls import path
from . import views

urlpatterns = [
    path('stations/', views.bus_stations, name='bus_stations'),  # Маршрут для отображения остановок
]