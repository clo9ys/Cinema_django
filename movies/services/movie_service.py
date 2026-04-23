from datetime import date

from rest_framework.exceptions import ValidationError

from ..dto import MovieCreateDTO, MovieUpdateDTO
from ..models import Genre, Movie


def get_movie_list_queryset():
    return Movie.objects.prefetch_related("genres").order_by("id")


def get_movie_by_id(movie_id):
    try:
        return Movie.objects.prefetch_related("genres").get(pk=movie_id)
    except Movie.DoesNotExist:
        raise ValidationError("Фильм не найден")



def assert_genre_pks_exist(pks):
    if not pks:
        return
    have = set(Genre.objects.filter(pk__in=pks).values_list("pk", flat=True))
    missing = set(pks) - have
    if missing:
        raise ValidationError(
            {"genre_ids": "Нет жанра с id: " + str(sorted(missing))}
        )


def build_create_dto(data: dict) -> MovieCreateDTO:
    raw = data.get("genre_ids") or []
    pks = tuple(int(x) for x in raw)
    return MovieCreateDTO(
        data["title"],
        data["summary"],
        data["release_year"],
        data["duration_minutes"],
        data["age_limit"],
        pks,
    )


def build_update_dto(data: dict) -> MovieUpdateDTO:
    d = MovieUpdateDTO()
    for key in (
        "title",
        "summary",
        "release_year",
        "duration_minutes",
        "age_limit",
    ):
        if key in data:
            setattr(d, key, data[key])
    if "genre_ids" in data:
        raw = data.get("genre_ids") or []
        d.genre_ids = tuple(int(x) for x in raw)
    return d


def _check_movie_invariants(
    title, summary, release_year, duration_minutes, age_limit
):
    t = (title or "").strip()
    if t == "":
        raise ValidationError({"title": "Название не может быть пустым"})
    if len(t) > 100:
        raise ValidationError(
            {"title": "Слишком длинное название"}
        )
    s = (summary or "").strip()
    if s == "":
        raise ValidationError(
            {"summary": "Описание не может быть пустым"},
        )
    now_y = date.today().year
    if release_year < 1896:
        raise ValidationError(
            {"release_year": "Слишком ранний год выхода"},
        )
    if release_year > now_y + 3:
        raise ValidationError(
            {
                "release_year": f"Год не может быть в будущем"
            },
        )
    if duration_minutes <= 0:
        raise ValidationError(
            {"duration_minutes": "Продолжительность должна быть больше нуля"},
        )
    if age_limit not in (0, 6, 12, 16, 18):
        raise ValidationError(
            {
                "age_limit": "Неверное возрастное ограничение",
            },
        )


def create_movie(dto: MovieCreateDTO) -> Movie:
    _check_movie_invariants(
        dto.title,
        dto.summary,
        dto.release_year,
        dto.duration_minutes,
        dto.age_limit,
    )
    m = Movie.objects.create(
        title=dto.title.strip(),
        summary=dto.summary.strip(),
        release_year=dto.release_year,
        duration_minutes=dto.duration_minutes,
        age_limit=dto.age_limit,
    )
    if dto.genre_ids:
        assert_genre_pks_exist(dto.genre_ids)
        m.genres.set(dto.genre_ids)
    return m


def update_movie(obj: Movie, dto: MovieUpdateDTO) -> Movie:
    title = dto.title if dto.title is not None else obj.title
    summ = dto.summary if dto.summary is not None else obj.summary
    ry = dto.release_year if dto.release_year is not None else obj.release_year
    dm = (
        dto.duration_minutes
        if dto.duration_minutes is not None
        else obj.duration_minutes
    )
    al = dto.age_limit if dto.age_limit is not None else obj.age_limit
    _check_movie_invariants(title, summ, ry, dm, al)
    if dto.title is not None:
        obj.title = title.strip()
    if dto.summary is not None:
        obj.summary = summ.strip()
    if dto.release_year is not None:
        obj.release_year = ry
    if dto.duration_minutes is not None:
        obj.duration_minutes = dm
    if dto.age_limit is not None:
        obj.age_limit = al
    obj.save()
    if dto.genre_ids is not None:
        assert_genre_pks_exist(tuple(dto.genre_ids))
        obj.genres.set(dto.genre_ids)
    return obj


def delete_movie(movie_id):
    try:
        m = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        raise ValidationError("Фильм не найден")
    m.delete()
