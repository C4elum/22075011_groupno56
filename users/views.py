# users/views.py
import logging
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.urls import reverse
from .forms import CustomRegistrationForm, LoginForm
from .forms import EditProfileForm  
from movies.models import Movie
from django.contrib.auth.models import User
from .models import Genre, WatchedMovie, Watchlist
from django.contrib import messages
from collections import Counter

from django.views.decorators.http import require_POST



def register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:select_genres')
    else:
        form = CustomRegistrationForm()

    return render(request, 'users/register.html', {'form': form})





def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if the user exists
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return render(request, 'users/login.html', {'form': form, 'error_message': 'Invalid username or password.'})

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('users:select_genres')
            else:
                return render(request, 'users/login.html', {'form': form, 'error_message': 'Invalid username or password.'})
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def select_genres(request):
    genres = Genre.objects.all()

    if request.method == 'POST':
        if 'random_movie' in request.POST:
            return redirect('movies:random_movie')

        selected_genres = request.POST.getlist('genres[]')
        num_recommendations = int(request.POST.get('num_recommendations', 10))
        print(selected_genres, num_recommendations)
        if not selected_genres:  # Check if no genres are selected
            error_msg = 'Please select at least one genre.'
            return render(request, 'users/select_genres.html', {'genres': genres, 'error_msg': error_msg})
        request.session['selected_genres'] = selected_genres
        return redirect('movies:recommendations', num_recommendations=num_recommendations)
   


    return render(request, 'users/select_genres.html', {'genres': genres})


@login_required
def user_profile(request):
    user = request.user
    watchlist_movies1= Watchlist.objects.filter(user=request.user).select_related('movie')
    watched_movies1 = WatchedMovie.objects.filter(user=request.user).select_related('movie')

    # Fetch the user's watched and watchlisted movies
    watchlist_movies = Watchlist.objects.filter(user=user).values_list('movie_id', flat=True)
    watched_movies = WatchedMovie.objects.filter(user=user).values_list('movie_id', flat=True)

    # Combine the movie IDs from both watchlist and watched movies
    user_movie_ids = set(list(watchlist_movies) + list(watched_movies))

    # Fetch the movies corresponding to the combined IDs
    user_movies = Movie.objects.filter(pk__in=user_movie_ids)

    # Extract genre information from the user's movies
    user_genres = []
    for movie in user_movies:
        if movie.genres:
            user_genres.extend(movie.genres.split())

    # Count genre occurrences
    genre_counts = Counter(user_genres)

    # Sort genres by count in descending order
    favorite_genres = [genre for genre, _ in genre_counts.most_common(3)]  # Change '3' to the desired number of favorite genres

    context = {
        'user': user,
        'watchlist_movies': watchlist_movies,
        'watched_movies': watched_movies,
        'watchlist_movies1': watchlist_movies1,
        'watched_movies1': watched_movies1,
        'favorite_genres': favorite_genres,
    }

    return render(request, 'users/profile.html', context)



@login_required
def user_logout(request):
    logout(request)
    return redirect('movies:main')








@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            if new_username != request.user.username and User.objects.filter(username=new_username).exists():
                messages.warning(request, 'Username already exists. Please choose a different one.')
            else:
                form.save()
                messages.success(request, 'Your profile has been updated.')  # Add a success message

                # Handle watched movies
                watched_movies = request.POST.getlist('watched_movies[]')
                ratings = request.POST.getlist('ratings[]')
                for i, movie_id in enumerate(watched_movies):
                    rating = ratings[i]
                    if rating:
                        WatchedMovie.objects.create(user=request.user, movie_id=movie_id, rating=rating)
                    else:
                        WatchedMovie.objects.create(user=request.user, movie_id=movie_id)

                # Handle unwatched movies
                unwatched_movies = Watchlist.objects.filter(user=request.user).exclude(id__in=watched_movies)
                unwatched_movies.delete()

                return redirect('users:user_profile')  # Redirect to the profile page
        else:
            messages.error(request, 'Your input is invalid.')  # Add an error message if the form is invalid

    else:
        form = EditProfileForm(instance=request.user)

    # Fetch movies from your database for the search bar
    query = request.GET.get('q')
    if query:
        movies = Movie.objects.filter(original_title__icontains=query)
    else:
        movies = Movie.objects.none()

    watchlist_movies = Watchlist.objects.filter(user=request.user)
    watched_movies = WatchedMovie.objects.filter(user=request.user).select_related('movie')  # Include the movie details

    context = {
        'form': form,
        'movies': movies,
        'watchlist_movies': watchlist_movies,
        'watched_movies': watched_movies,
    }

    return render(request, 'users/edit_profile.html', context)

@require_POST
@login_required
def move_to_watched(request):
    movie_id = request.POST.get('movie_id')
    rating = request.POST.get('rating')
    movie = Movie.objects.get(id=movie_id)

    if rating:
        watched_movie, created = WatchedMovie.objects.get_or_create(user=request.user, movie=movie)
        watched_movie.rating = rating
        watched_movie.save()

        # Delete the movie from the watchlist
        Watchlist.objects.filter(movie=movie, user=request.user).delete()

        response_data = {
            'success': True,
            'movie_title': movie.original_title,
        }
        return JsonResponse(response_data)
    else:
        response_data = {
            'success': False,
            'message': 'Please enter a valid rating.',
        }
        return JsonResponse(response_data)
