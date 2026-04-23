from rest_framework.exceptions import ValidationError

from ..dto import GenreCreateDTO, GenreUpdateDTO
from ..models import Genre


def get_genre_queryset():
    return Genre.objects.order_by("id")


def get_genre_by_id(gid: int) -> Genre:
    try:
        return Genre.objects.get(pk=gid)
    except Genre.DoesNotExist:
        raise ValidationError("Жанр не найден.")


def create_genre(dto: GenreCreateDTO) -> Genre:
    name = dto.name.strip()
    if not name:
        raise ValidationError("Название жанра не может быть пустым")
    old = Genre.objects.filter(name__iexact=name)
    if old.exists():
        raise ValidationError(
            "Жанр с таким названием уже существует"
        )
    return Genre.objects.create(name=name)


def update_genre(gid, dto: GenreUpdateDTO) -> Genre:
    g = get_genre_by_id(gid)
    name = dto.name.strip()
    if not name:
        raise ValidationError("Название жанра не может быть пустым")
    oth = Genre.objects.filter(name__iexact=name).exclude(pk=g.pk)
    if oth.exists():
        raise ValidationError(
            "Жанр с таким названием уже существует"
        )
    g.name = name
    g.save()
    return g


def delete_genre(gid) -> None:
    g = get_genre_by_id(gid)
    g.delete()
