# users/models.py
from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class Genre(models.Model):
    name = models.CharField(max_length=25)


    def __str__(self):
        return self.name


# List of genres
genre_names = [
    "Western", "Thriller", "Science Fiction", "Music", "Romance",
    "Horror", "History", "War", "Drama", "Foreign",
    "Comedy", "Adventure", "Documentary", "Crime", "Animation",
    "Family", "Action", "Fantasy", "Mystery", "TV", "Movie"
]

# Create instances of Genre for each genre if they don't exist
for genre_name in genre_names:
    Genre.objects.get_or_create(name=genre_name)



class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    
