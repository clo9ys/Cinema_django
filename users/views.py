from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.subscription_service import SubscriptionService
from .models import WatchList
from .serializers import WatchListSerializer
from .dto import SubscriptionData


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


class UserViewSet(viewsets.ViewSet):
    sub_service = SubscriptionService()

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        dto = SubscriptionData(
            user_id=int(pk),
            sub_id=request.data.get("sub_id"),
        )

        self.sub_service.subscribe_user(dto)
        return Response({"status": "success", "message": "Подписка обновлена"}, status=status.HTTP_200_OK)
