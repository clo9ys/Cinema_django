from django.contrib import admin
from .models import Genre, Movie

admin.site.register(Genre)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'age_limit', 'duration_minutes')

    list_filter = ('genres', 'release_year', 'age_limit')

    search_fields = ('title', 'summary')

    filter_horizontal = ('genres',)
