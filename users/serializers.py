from django.contrib.auth.models import User
from movies.serializers import MovieSerializer
from .models import Subscription, UserProfile
from rest_framework import serializers
from .models import WatchList
from movies.models import Movie


class WatchListSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WatchList
        fields = ['id', 'movie_id', 'added_at']
        read_only_fields = ['id', 'added_at']

    def validate_movie_id(self, value):
        """существует ли фильм с таким id"""
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Фильм с таким id не существует")
        return value

    def validate(self, data):
        """не добавлен ли уже фильм в избранное"""
        user = self.context['request'].user
        movie_id = data.get('movie_id')

        if WatchList.objects.filter(user=user, movie_id=movie_id).exists():
            raise serializers.ValidationError("Этот фильм уже в вашем избранном")

        return data


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
        """Возраст"""
        if value <= 0:
            raise serializers.ValidationError("Возраст не может быть отрицательным или нулевым.")
        return value

    def validate(self, attrs) -> dict:
        """Один пользователь — один профиль"""
        user = attrs.get("user")
        exist = UserProfile.objects.filter(user=user)
        if self.instance:
            exist = exist.exclude(pk=self.instance.pk)
        if exist.exists():
            raise serializers.ValidationError("У этого пользователя уже есть профиль.")
        return attrs


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

    def validate(self, attrs) -> dict:
        """Пользователь + фильм в избранном не должны повторяться"""
        user = attrs.get("user")
        movie = attrs.get("movie")
        if self.instance:
            if user is None:
                user = self.instance.user
            if movie is None:
                movie = self.instance.movie
        if user is None or movie is None:
            return attrs
        exists = WatchList.objects.filter(user=user, movie=movie)
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise serializers.ValidationError("Такая запись в избранном уже есть.")
        return attrs
