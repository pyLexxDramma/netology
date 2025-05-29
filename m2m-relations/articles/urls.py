from django.urls import path
from . import views

urlpatterns = [
    path('', views.articles_list, name='articles_list'),
    path('tag/<int:pk>/', views.tag_detail, name='tag_detail'),
]