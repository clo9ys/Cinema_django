from django.test import TestCase
from datetime import date
from rest_framework.exceptions import ValidationError

from .models import Movie, Genre
from .dto import MovieCreateDTO, MovieUpdateDTO, GenreCreateDTO, GenreUpdateDTO

from .services.movie_service import (
    get_movie_by_id, assert_genre_pks_exist,
    build_create_dto, _check_movie_invariants,
    create_movie, update_movie, delete_movie
)
from .services.genre_service import get_genre_by_id, create_genre, update_genre, delete_genre


class GenreServiceTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Drama")

    def test_get_genre_by_id_success(self):
        genre = get_genre_by_id(self.genre.id)
        self.assertEqual(genre.name, "Drama")

    def test_get_genre_by_id_not_found(self):
        with self.assertRaisesMessage(ValidationError, "Жанр не найден."):
            get_genre_by_id(999)

    def test_create_genre_success(self):
        dto = GenreCreateDTO(name="  Comedy  ") # проверка strip
        genre = create_genre(dto)
        self.assertEqual(genre.name, "Comedy")
        self.assertEqual(Genre.objects.count(), 2)

    def test_create_genre_duplicate_case_insensitive(self):
        dto = GenreCreateDTO(name="DRAMA")
        with self.assertRaisesMessage(ValidationError, "Жанр с таким названием уже существует"):
            create_genre(dto)

    def test_update_genre_success(self):
        dto = GenreUpdateDTO()
        dto.name = "Tragedy"
        genre = update_genre(self.genre.id, dto)
        self.assertEqual(genre.name, "Tragedy")

    def test_update_genre_duplicate(self):
        Genre.objects.create(name="Horror")
        dto = GenreUpdateDTO()
        dto.name = "horror"
        with self.assertRaisesMessage(ValidationError, "Жанр с таким названием уже существует"):
            update_genre(self.genre.id, dto)

    def test_delete_genre(self):
        delete_genre(self.genre.id)
        self.assertEqual(Genre.objects.count(), 0)


class MovieServiceTest(TestCase):
    def setUp(self):
        self.genre1 = Genre.objects.create(name="g1")
        self.genre2 = Genre.objects.create(name="g2")
        self.movie = Movie.objects.create(
            title="name",
            summary="...",
            release_year=2000,
            duration_minutes=120,
            age_limit=16
        )
        self.movie.genres.add(self.genre1, self.genre2)

    def test_get_movie_by_id_success(self):
        movie = get_movie_by_id(self.movie.id)
        self.assertEqual(movie.title, "name")

    def test_get_movie_by_id_not_found(self):
        with self.assertRaisesMessage(ValidationError, "Фильм не найден"):
            get_movie_by_id(9999)

    def test_assert_genre_pks_exist_fails(self):
        with self.assertRaises(ValidationError) as context:
            assert_genre_pks_exist([self.genre1.id, 999])
        self.assertIn("Нет жанра с id", str(context.exception))

    def test_build_create_dto(self):
        data = {
            "title": "new name",
            "summary": "sss",
            "release_year": 2020,
            "duration_minutes": 120,
            "age_limit": 18,
            "genre_ids": [str(self.genre1.id)]
        }
        dto = build_create_dto(data)
        self.assertEqual(dto.title, "new name")
        self.assertEqual(dto.genre_ids, (self.genre1.id,))

    def test_check_movie_invariants_invalid_year(self):
        with self.assertRaisesMessage(ValidationError, "Слишком ранний год выхода"):
            _check_movie_invariants("T", "S", 1111, 120, 18)

        with self.assertRaisesMessage(ValidationError, "Год не может быть в будущем"):
            _check_movie_invariants("T", "S", 2222, 120, 18)

    def test_check_movie_invariants_invalid_age(self):
        with self.assertRaisesMessage(ValidationError, "Неверное возрастное ограничение"):
            _check_movie_invariants("T", "S", 2020, 120, 14)

    def test_create_movie(self):
        dto = MovieCreateDTO(
            title="newnewname",
            summary="newsss",
            release_year=2010,
            duration_minutes=140,
            age_limit=12,
            genre_ids=(self.genre2.id,)
        )
        movie = create_movie(dto)
        self.assertEqual(Movie.objects.count(), 2)
        self.assertEqual(movie.title, "newnewname")
        self.assertIn(self.genre2, movie.genres.all())

    def test_update_movie(self):
        dto = MovieUpdateDTO()
        dto.title = "namename"
        dto.release_year = 2003
        updated_movie = update_movie(self.movie, dto)
        self.assertEqual(updated_movie.title, "namename")
        self.assertEqual(updated_movie.release_year, 2003)
        self.assertEqual(updated_movie.age_limit, 16)

    def test_delete_movie(self):
        delete_movie(self.movie.id)
        self.assertEqual(Movie.objects.count(), 0)
