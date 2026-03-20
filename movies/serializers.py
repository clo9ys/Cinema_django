from datetime import date
from rest_framework import serializers
from .models import Genre, Movie


class GenreSerializer(serializers.ModelSerializer):
    """Жанр каталога: id и название."""

    class Meta:
        model = Genre
        fields = ["id", "name"]

    def validate_name(self, value) -> str:
        """Жанр не пуст и не дублируется"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Укажите название жанра.")
        existing = Genre.objects.filter(name__iexact=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("Такой жанр уже существует.")
        return value


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        write_only=True,
        required=False,
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

    def validate_title(self, value) -> str:
        """Название не пустое, длина не больше 200 символов"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Название не может быть пустым.")
        if len(value) > 200:
            raise serializers.ValidationError("Название не должно превышать 200 символов.")
        return value

    def validate_summary(self, value) -> str:
        """Описание фильма не пустое"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Описание фильма не может быть пустым.")
        return value

    def validate_release_year(self, value) -> int:
        """Год от 1896("Прибытие поезда") и до ближайшего будущего ( + 3 года)"""
        now = date.today().year
        if value < 1896:
            raise serializers.ValidationError("Год выпуска не может быть раньше 1896.")
        if value > now + 3:
            raise serializers.ValidationError(f"Год выпуска не может быть позже {now + 3}.")
        return value

    def validate_duration_minutes(self, value) -> int:
        """Длительность в минутах больше нуля"""
        if value <= 0:
            raise serializers.ValidationError("Продолжительность должна быть больше 0.")
        return value

    def validate_age_limit(self, value) -> int:
        """Возрастной рейтинг только из допустимых значений"""
        allowed = {choice[0] for choice in Movie.AGE_LIMIT_CHOICES}
        if value not in allowed:
            raise serializers.ValidationError("Недопустимое возрастное ограничение.")
        return value

    def create(self, validated_data) -> Movie:
        """Создаём фильм и вешаем жанры по списку id"""
        genre_ids = validated_data.pop("genre_ids", [])
        movie = Movie.objects.create(**validated_data)
        if genre_ids:
            movie.genres.set(genre_ids)
        return movie

    def update(self, instance, validated_data) -> Movie:
        """Обновляем поля; если передали genre_ids — перезаписываем жанры"""
        genre_ids = validated_data.pop("genre_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genre_ids is not None:
            instance.genres.set(genre_ids)
        return instance
