from django_filters import rest_framework as filters
from .models import Movie


class MovieFilter(filters.FilterSet):
    # Фильтр по жанру (по id)
    genre = filters.NumberFilter(field_name='genres__id')

    # Опционально: фильтр по названию жанра
    genre_name = filters.CharFilter(field_name='genres__name', lookup_expr='exact')

    # Фильтр по году выпуска
    release_year = filters.NumberFilter(field_name='release_year')

    class Meta:
        model = Movie
        fields = ['genre', 'genre_name', 'release_year']