from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name="Жанр")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Movie(models.Model):
    AGE_LIMIT_CHOICES = [
        (0, '0+'),
        (6, '6+'),
        (12, '12+'),
        (16, '16+'),
        (18, '18+')
    ]

    title = models.CharField(max_length=100, verbose_name="Название фильма")
    summary = models.TextField(verbose_name="Аннотация")
    release_year = models.PositiveIntegerField(verbose_name="Год выхода")
    duration_minutes = models.PositiveIntegerField(verbose_name="Продолжительность (минуты)")

    age_limit = models.PositiveIntegerField(choices=AGE_LIMIT_CHOICES, default=0, verbose_name="Возрастное ограничение")

    genres = models.ManyToManyField(Genre, related_name="movies", verbose_name="Жанры")

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title