from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),  # Главная страница
    path('<str:recipe_name>/', views.recipe_view, name='recipe'),
]