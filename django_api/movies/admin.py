from django.contrib import admin
from .models import Genre, Movie
from .services.notification_service import notify_fastapi_about_new_movie

admin.site.register(Genre)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'age_limit', 'duration_minutes')

    list_filter = ('genres', 'release_year', 'age_limit')

    search_fields = ('title', 'summary')

    filter_horizontal = ('genres',)

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new:
            notify_fastapi_about_new_movie(obj)
