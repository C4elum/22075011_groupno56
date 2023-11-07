from functools import reduce
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie
from django.db.models import Count, Q, F,Count, Case, When
from django.contrib.auth.decorators import login_required
from users.models import WatchedMovie, Watchlist, Genre
from django.contrib import messages
from django.db.models import Case, When

from operator import or_




from django.http import JsonResponse

# @login_required
# def get_movie_details(request, movie_id):
#     movie = Movie.objects.get(pk=movie_id)
#     context = {'movie': movie}
#     return render(request, 'movies/movie_details_partial.html', context)


def main(request):
    return render(request, 'movies/main.html')



def movie_list(request):
    movies = Movie.objects.all()
    watched_movie_ids = WatchedMovie.objects.filter(user=request.user).values_list('movie_id', flat=True)
    watchlist_movie_ids = Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True)

    watched_movies = []
    watchlist_movies = []

    for movie in movies:
        if movie.id in watched_movie_ids:
            watched_movies.append(movie)
        elif movie.id in watchlist_movie_ids:
            watchlist_movies.append(movie)

    print(watched_movie_ids)  # Debugging statement
    print(watchlist_movie_ids) 
    context = {
        'movies': movies,
        'watched_movies': watched_movies,
        'watchlist_movies': watchlist_movies,
    }

    return render(request, 'movies/movie_list.html', context)


def movie_detail(request, movie_id):
    
    movie = Movie.objects.get(pk=movie_id)
   
    watchlist_movies = Watchlist.objects.filter(user=request.user)
    watched_movies = WatchedMovie.objects.filter(user=request.user)
    watched_movie_ids = WatchedMovie.objects.filter(user=request.user).values_list('movie_id', flat=True)
    watchlist_movie_ids = Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True)


    context = {
        
    'movie': movie,
    'watchlist_movies': watchlist_movies,
    'watched_movies': watched_movies,
    'watchlist_movie_ids': watchlist_movie_ids,
    'watched_movie_ids': watched_movie_ids,
    }



    # Render a template with movie details
    return render(request, 'movies/movie_detail.html', context)






def movie_details(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    watchlist_movies = Watchlist.objects.filter(user=request.user, movie=movie)
    watched_movies = WatchedMovie.objects.filter(user=request.user, movie=movie)

    context = {
        'movie': movie,
        'watchlist_movies': watchlist_movies,
        'watched_movies': watched_movies,
    }

    return render(request, 'movies/movie_details.html', context)



@login_required
def movie_recommendations(request, num_recommendations=10):
    
    


    selected_genres = request.session.get('selected_genres', [])
    if selected_genres:
        selected_genre_names = Genre.objects.filter(id__in=selected_genres).values_list('name', flat=True)
        q_objects = [Q(genres__icontains=f" {genre} ") | Q(genres__istartswith=f"{genre} ") | Q(genres__iendswith=f" {genre}") | Q(genres__exact=genre) for genre in selected_genre_names]
    else:
        q_objects = []
    # Get a list of watched and watchlisted movie IDs
    watched_movie_ids = WatchedMovie.objects.filter(user=request.user).values_list('movie_id', flat=True)
    watchlist_movie_ids = Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True)



    
    # Get recommended movies that contain any of the selected genres and haven't been watched or watchlisted yet
    
    recommended_movies = Movie.objects.filter(
        reduce(or_, q_objects)
    ).exclude(id__in=watched_movie_ids).exclude(id__in=watchlist_movie_ids)

    # Annotate with the count of matched selected genres
    recommended_movies = recommended_movies.annotate(
        num_matched_selected_genres=Count(Case(*[When(genres__icontains=f" {genre} ", then=1) for genre in selected_genre_names]))
    )

    # Sort movies by the number of matched selected genres in descending order, then by vote_average
    recommended_movies = recommended_movies.order_by(
        '-num_matched_selected_genres',
        '-vote_average'
    )[:num_recommendations]

    for movie in recommended_movies:
        print(f"Movie Title: {movie.original_title}")
        print(f"Matched Selected Genres: {movie.num_matched_selected_genres}")
        print(f"Movie id: {movie.imdb_id}")

    # # Fetch the user's watchlist and watched movies
    # watchlist_movies = Watchlist.objects.filter(user=request.user, movie__in=recommended_movies).values_list('movie_id', flat=True)
    # watched_movies = WatchedMovie.objects.filter(user=request.user, movie__in=recommended_movies).values_list('movie_id', flat=True)
    watchlist_movies = Watchlist.objects.filter(user=request.user, movie__in=recommended_movies)
    watched_movies = WatchedMovie.objects.filter(user=request.user, movie__in=recommended_movies)


    context = {
        'genres': selected_genre_names,
        'recommended_movies': recommended_movies,
        'watchlist_movies': watchlist_movies,
        'watched_movies': watched_movies,
        
    }
   
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        action = request.POST.get('action')

        if movie_id and action:
            try:
                movie = Movie.objects.get(id=movie_id)
                if action == 'watchlist':
                    Watchlist.objects.get_or_create(user=request.user, movie=movie)
                    # Remove the movie from recommended movies
                    recommended_movies = recommended_movies.exclude(id=movie_id)
                    messages.success(request, f'{movie.original_title} has been added to your watchlist!')
                elif action == 'watched':
                    rating = request.POST.get('rating')
                    if not rating:
                        messages.error(request, 'Please provide a rating before adding to watched.')
                    else:
                        WatchedMovie.objects.get_or_create(user=request.user, movie=movie, rating=rating)
                        # Remove the movie from recommended movies
                        recommended_movies = recommended_movies.exclude(id=movie_id)
                        messages.success(request, f'{movie.original_title} has been added to your watched list!')
            except Movie.DoesNotExist:
                pass

    context['recommended_movies'] = recommended_movies

    # Return the context or render a template with the context
    return render(request, 'movies/recommendations.html', context)

from random import choice

@login_required
def random_movie(request):
    # Get the user's watched and watchlist movies
    watched_movies = WatchedMovie.objects.filter(user=request.user).values_list('movie', flat=True)
    watchlist_movies = Watchlist.objects.filter(user=request.user).values_list('movie', flat=True)
   
    watched_movie_ids = WatchedMovie.objects.filter(user=request.user).values_list('movie_id', flat=True)
    watchlist_movie_ids = Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True)
    
    # Get a random movie that the user hasn't watched or added to the watchlist
    random_movie = Movie.objects.exclude(id__in=watched_movies).exclude(id__in=watchlist_movies).order_by('?').first()

    context = {
        'random_movie': random_movie,
        'watchlist_movies': watchlist_movies,
        'watched_movies': watched_movies,
        'watchlist_movie_ids': watchlist_movie_ids,
        'watched_movie_ids': watched_movie_ids,
    }

    return render(request, 'movies/random_movie.html', context)






@login_required
def add_to_watchlist(request, movie_id):
    # Get the Movie object with the given `movie_id`
    movie = get_object_or_404(Movie, pk=movie_id)

    # Check if the user already has this movie in their watchlist
    if Watchlist.objects.filter(user=request.user, movie=movie).exists():
        messages.info(request, 'Movie is already in your watchlist.')
    else:
        # Add the movie to the user's watchlist
        Watchlist.objects.create(user=request.user, movie=movie)
        messages.success(request, 'Movie added to your watchlist successfully.')


    return redirect(request.META.get('HTTP_REFERER', 'movies:random-movie'))






@login_required
def add_to_watched(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        watched_movie, created = WatchedMovie.objects.get_or_create(user=request.user, movie=movie, defaults={'rating': rating})
        if not created:
            watched_movie.rating = rating
            watched_movie.save()

        # Check if the movie exists in the user's watchlist
        watchlist_movie = Watchlist.objects.filter(user=request.user, movie_id=movie_id).first()
        if watchlist_movie:
            watchlist_movie.delete()

    # Redirect to the previous page after performing the action
    return redirect(request.META.get('HTTP_REFERER', 'movies:movie-list'))



