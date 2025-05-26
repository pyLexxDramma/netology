from django.urls import path, register_converter
from . import views, converters

register_converter(converters.DateConverter, 'dt')

urlpatterns = [
    path('', views.books_list, name='books_list'),
    path('<dt:pub_date>/', views.books_by_date, name='books_by_date'),
]