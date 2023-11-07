from django.contrib import admin

# Register your models here.
from .models import Genre, Watchlist, WatchedMovie

admin.site.register(Genre)
admin.site.register(Watchlist)
admin.site.register(WatchedMovie)