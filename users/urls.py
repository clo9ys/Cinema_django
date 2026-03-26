from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WatchListViewSet

router = DefaultRouter()
router.register('watchlist', WatchListViewSet, basename="watchlist")

urlpatterns = [
    path('', include(router.urls)),
]
