from django.test import TestCase
from django.http import Http404
from django.contrib.auth.models import User

from .models import UserProfile, WatchList, Subscription
from movies.models import Movie
from config.exceptions import AgeLimitError, AlreadySubscribedError
from .dto import WatchListData, SubscriptionData
from .services.watchlist_service import WatchListService
from .services.subscription_service import SubscriptionService


class WatchListServiceTest(TestCase):
    def setUp(self):
        self.service = WatchListService()
        self.user = User.objects.create(username="viewer")
        self.profile = UserProfile.objects.create(user=self.user, age=20)

        self.movie = Movie.objects.create(
            title="Adult Movie",
            summary="...",
            release_year=2020,
            duration_minutes=100,
            age_limit=18
        )
        self.data = WatchListData(user_id=self.user.id, movie_id=self.movie.id)

    def test_add_movie_to_watchlist_success(self):
        self.profile.age = 21
        self.profile.save()

        watchlist_item = self.service.add_movie_to_watchlist(self.data)
        self.assertEqual(watchlist_item.user, self.user)
        self.assertEqual(watchlist_item.movie, self.movie)
        self.assertEqual(WatchList.objects.count(), 1)

    def test_add_movie_to_watchlist_age_limit_error(self):
        self.profile.age = 16
        self.profile.save()

        with self.assertRaises(AgeLimitError) as context:
            self.service.add_movie_to_watchlist(self.data)
        self.assertIn("только для", str(context.exception))


class SubscriptionServiceTest(TestCase):
    def setUp(self):
        self.service = SubscriptionService()
        self.user = User.objects.create(username="testuser")
        self.profile = UserProfile.objects.create(user=self.user, age=25)
        self.plan = Subscription.objects.create(name="premium", price=99)
        self.data = SubscriptionData(user_id=self.user.id, sub_id=self.plan.id)

    def test_subscribe_user_success(self):
        profile = self.service.subscribe_user(self.data)
        self.assertEqual(profile.subscription, self.plan)
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_subscribe_user_already_subscribed(self):
        self.service.subscribe_user(self.data)

        # оформление подписки во второй раз
        with self.assertRaises(AlreadySubscribedError) as context:
            self.service.subscribe_user(self.data)
        self.assertIn("уже есть подписка", str(context.exception))

    def test_subscribe_user_not_found(self):
        invalid_data = SubscriptionData(user_id=999, sub_id=self.plan.id)
        with self.assertRaises(Http404):
            self.service.subscribe_user(invalid_data)
