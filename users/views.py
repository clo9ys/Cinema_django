from django.shortcuts import render

# Create your views here.


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import WatchList
from .serializers import WatchListSerializer


class WatchListViewSet(viewsets.ModelViewSet):
    """
    viewSet для работы с watchlist
    """
    serializer_class = WatchListSerializer
    permission_classes = [IsAuthenticated]  # только авторизованные пользователи

    def get_queryset(self):
        """возвращает избранное пользователя"""
        return WatchList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """при создании подставляет пользователя"""
        serializer.save(user=self.request.user)
