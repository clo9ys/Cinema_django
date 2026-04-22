from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Subscription, UserProfile, WatchList
from config.exceptions import AlreadySubscribedError, AgeLimitError
from .dto import SubscriptionData, WatchListData
from movies.models import Movie


class SubscriptionService:
    @transaction.atomic
    def subscribe_user(self, data: SubscriptionData):
        user = get_object_or_404(User, id=data.user_id)
        plan = get_object_or_404(Subscription, id=data.sub_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)

        if profile.subscription == plan:
            raise AlreadySubscribedError(f"У пользователя уже есть подписка {plan.name}")

        profile.subscription = plan
        profile.save()
        return profile


class WatchListService:
    @transaction.atomic
    def add_movie_to_watchlist(self, data: WatchListData):
        movie = get_object_or_404(Movie, id=data.movie_id)

        user = get_object_or_404(User, id=data.user_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        user_age = profile.age

        if user_age <= movie.age_limit:
            raise AgeLimitError

        return WatchList.objects.create(user=user, movie=movie)
