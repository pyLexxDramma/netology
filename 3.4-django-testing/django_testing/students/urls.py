from django.urls import path
from rest_framework.routers import DefaultRouter

from students.views import CoursesViewSet

router = DefaultRouter()
router.register(r'courses', CoursesViewSet, basename='course')

urlpatterns = router.urls