from rest_framework import viewsets
from rest_framework.response import Response

from .dto import GenreCreateDTO, GenreUpdateDTO
from .filters import MovieFilter
from .serializers import GenreSerializer, MovieSerializer
from .services import genre_service, movie_service


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    filterset_class = MovieFilter
    search_fields = ["title"]

    def get_queryset(self):
        return movie_service.get_movie_list_queryset()

    def get_object(self):
        pk = self.kwargs["pk"]
        return movie_service.get_movie_by_id(pk)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        m = movie_service.create_movie(
            movie_service.build_create_dto(ser.validated_data)
        )
        data = self.get_serializer(m).data
        return Response(
            data, status=201, headers=self.get_success_headers(data)
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        old = self.get_object()
        ser = self.get_serializer(old, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        m = movie_service.update_movie(
            old, movie_service.build_update_dto(ser.validated_data)
        )
        return Response(self.get_serializer(m).data)

    def destroy(self, request, *args, **kwargs):
        movie_service.delete_movie(self.kwargs["pk"])
        return Response(status=204)


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer

    def get_queryset(self):
        return genre_service.get_genre_queryset()

    def get_object(self):
        return genre_service.get_genre_by_id(self.kwargs["pk"])

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = GenreCreateDTO(name=ser.validated_data["name"])
        g = genre_service.create_genre(dto)
        data = self.get_serializer(g).data
        return Response(
            data, status=201, headers=self.get_success_headers(data)
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        old = self.get_object()
        ser = self.get_serializer(old, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        n = ser.validated_data.get("name", old.name)
        g = genre_service.update_genre(old.pk, GenreUpdateDTO(name=n))
        return Response(self.get_serializer(g).data)

    def destroy(self, request, *args, **kwargs):
        genre_service.delete_genre(self.kwargs["pk"])
        return Response(status=204)
