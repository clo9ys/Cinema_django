from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet

router = DefaultRouter()
router.register('movies', MovieViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
