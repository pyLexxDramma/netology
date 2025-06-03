from django.urls import path
from .views import SensorListCreateView, SensorRetrieveUpdateView, MeasurementCreateView

urlpatterns = [
    path('sensors/', SensorListCreateView.as_view(), name='sensor-list-create'),
    path('sensors/<int:pk>/', SensorRetrieveUpdateView.as_view(), name='sensor-retrieve-update'),
    path('measurements/', MeasurementCreateView.as_view(), name='measurement-create'),
]
