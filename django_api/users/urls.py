from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WatchListViewSet, UserViewSet

router = DefaultRouter()
router.register(r'watchlist', WatchListViewSet, basename="watchlist")
router.register(r'users', UserViewSet, basename="user")

urlpatterns = [
    path('', include(router.urls)),
]
