from rest_framework import viewsets

from .filters import MovieFilter
from .models import Movie
from .serializers import MovieSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.prefetch_related('genres').all()
    serializer_class = MovieSerializer
    filterset_class = MovieFilter
    search_fields = ['title']
