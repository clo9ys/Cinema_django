from django.contrib.auth.models import User
from rest_framework import serializers
from movies.models import Movie
from movies.serializers import MovieSerializer
from .models import Subscription, UserProfile, WatchList


class UserSerializer(serializers.ModelSerializer):
    """Пользователь"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only = ["id"]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Подписка: название, описание, цена."""

    class Meta:
        model = Subscription
        fields = ["id", "name", "description", "price"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Профиль: пользователь, возраст, подписка"""

    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ["id", "user", "user_id", "age", "subscription"]
        read_only = ["id"]

    def __init__(self, *args, **kwargs):
        """При создании записи user_id обязателен!!!"""
        super().__init__(*args, **kwargs)
        if self.instance is None:
            self.fields["user_id"].required = True

    def validate_age(self, value) -> int:
        """Возрастъ"""
        if value <= 0:
            raise serializers.ValidationError("Возраст не может быть отрицательным или нулевым.")
        return value

    def validate_profile(self, data) -> dict:
        """Один пользователь — один профиль"""
        user = data.get("user")
        exist = UserProfile.objects.filter(user=user)
        if self.instance:
            exist = exist.exclude(pk=self.instance.pk)
        if exist.exists():
            raise serializers.ValidationError("У этого пользователя уже есть профиль.")
        return data


class WatchListSerializer(serializers.ModelSerializer):
    """Избранное: пользователь + фильм"""

    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False,
    )
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True,
        required=False,
    )

    class Meta:
        model = WatchList
        fields = ["id", "user", "user_id", "movie", "movie_id", "added_at"]
        read_only = ["id", "added_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None:
            self.fields["user_id"].required = True
            self.fields["movie_id"].required = True

    def validate_watchlist(self, data) -> dict:
        """Пользователь + фильм в избранном не должны повторяться"""
        user = data.get("user")
        movie = data.get("movie")
        if self.instance:
            if user is None:
                user = self.instance.user
            if movie is None:
                movie = self.instance.movie
        if user is None or movie is None:
            return data
        exists = WatchList.objects.filter(user=user, movie=movie)
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise serializers.ValidationError("Такая запись в избранном уже есть.")
        return data
