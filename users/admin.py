from django.contrib import admin
from .models import Subscription, UserProfile, WatchList

admin.site.register(Subscription)
admin.site.register(UserProfile)
admin.site.register(WatchList)