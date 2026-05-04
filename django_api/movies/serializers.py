from datetime import date
from rest_framework import serializers
from .models import Genre, Movie
from .services import movie_service


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]

    def validate_name(self, value):
        value = value.strip()
        if value == "":
            raise serializers.ValidationError("Введите название жанра")
        return value


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "summary",
            "release_year",
            "duration_minutes",
            "age_limit",
            "genres",
            "genre_ids",
        ]

    def validate_genre_ids(self, value):
        if not value:
            return []
        t = tuple(int(x) for x in value)
        movie_service.assert_genre_pks_exist(t)
        return value

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Название не может быть пустым")
        if len(value) > 100:
            raise serializers.ValidationError("Название слишком длинное")
        return value

    def validate_summary(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Укажите описание")
        return value

    def validate_release_year(self, value):
        y = date.today().year
        if value < 1896:
            raise serializers.ValidationError("Слишком ранний год выхода")
        if value > y + 3:
            raise serializers.ValidationError("Год выхода не может быть в будущем")
        return value

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Продолжительность должна быть больше 0")
        return value

    def validate_age_limit(self, value):
        ok = [0, 6, 12, 16, 18] 
        if value not in ok:
            raise serializers.ValidationError("Неверное возрастное ограничение")
        return value
