from django.db import models
from django.contrib.auth.models import User

class Subscription(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название подписки")
    description = models.TextField(verbose_name="Что входит в подписку")
    price = models.PositiveIntegerField(verbose_name="Цена подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    age = models.PositiveIntegerField(verbose_name="Возраст пользователя")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Подписка")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.user.username


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist", verbose_name="Пользователь")
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name="watchlisted_by", verbose_name="Фильм")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user.username} -> {self.movie.title}"