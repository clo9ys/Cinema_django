from dataclasses import dataclass


@dataclass
class SubscriptionData:
    user_id: int
    sub_id: int


@dataclass
class WatchListData:
    user_id: int
    movie_id: int
