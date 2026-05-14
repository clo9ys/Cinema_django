from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.subscription_service import SubscriptionService
from .services.watchlist_service import WatchListService
from .models import WatchList
from .serializers import WatchListSerializer
from .dto import SubscriptionData, WatchListData
from movies.models import Movie
from movies.serializers import MovieSerializer

_watchlist_service = WatchListService()


class WatchListViewSet(viewsets.ModelViewSet):
    serializer_class = WatchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WatchList.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        movie_id = request.data.get("movie_id")
        if not movie_id:
            raise ValidationError({"movie_id": "Обязательное поле"})
        dto = WatchListData(user_id=request.user.id, movie_id=int(movie_id))
        item = _watchlist_service.add_movie_to_watchlist(dto)
        return Response(self.get_serializer(item).data, status=status.HTTP_201_CREATED)


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


@api_view(['GET'])
def recommendations(request, user_id):
    last_item = (
        WatchList.objects.filter(user_id=user_id)
        .select_related("movie")
        .order_by("-added_at")
        .first()
    )
    if not last_item:
        return Response([])

    genre_ids = list(last_item.movie.genres.values_list("id", flat=True))
    movies = (
        Movie.objects.filter(genres__id__in=genre_ids)
        .exclude(id=last_item.movie_id)
        .prefetch_related("genres")
        .distinct()
        .order_by("id")
    )
    return Response(MovieSerializer(movies, many=True).data)
