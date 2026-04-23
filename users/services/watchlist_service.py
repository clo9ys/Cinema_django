from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models import UserProfile, WatchList
from config.exceptions import AgeLimitError
from ..dto import WatchListData
from movies.models import Movie


class WatchListService:
    @transaction.atomic
    def add_movie_to_watchlist(self, data: WatchListData):
        movie = get_object_or_404(Movie, id=data.movie_id)

        user = get_object_or_404(User, id=data.user_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        user_age = profile.age

        if user_age <= movie.age_limit:
            raise AgeLimitError(f"Фильм {movie.title} только для {movie.age_limit}")

        return WatchList.objects.create(user=user, movie=movie)
