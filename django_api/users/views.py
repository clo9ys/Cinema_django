from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.subscription_service import SubscriptionService
from .models import WatchList
from .serializers import WatchListSerializer
from .dto import SubscriptionData
from movies.models import Movie
from movies.serializers import MovieSerializer


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


def recommendations(request, user_id):
    last_item = (
        WatchList.objects.filter(user_id=user_id)
        .select_related("movie")
        .order_by("-added_at")
        .first()
    )
    if not last_item:
        return Response([])

    genre_ids = list(
        last_item.movie.genres.values_list("id", flat=True)
    )
    movies = (
        Movie.objects.filter(genres__id__in=genre_ids)
        .exclude(id=last_item.movie_id)
        .prefetch_related("genres")
        .distinct()
        .order_by("id")
    )
    return Response(MovieSerializer(movies, many=True).data)
