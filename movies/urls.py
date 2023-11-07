from django.urls import path
from . import views
app_name = 'movies' 
urlpatterns = [
    path('main', views.main, name='main'),
    path('movie_list', views.movie_list, name='movie-list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie-detail'),
    path('recommendations/', views.movie_recommendations, name='recommendations'),
    path('recommendations/<int:num_recommendations>', views.movie_recommendations, name='recommendations'),
    path('add_to_watchlist/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('add_to_watched/<int:movie_id>/', views.add_to_watched, name='add_to_watched'),
    path('randommovie/', views.random_movie, name='random_movie'),
    path('movie_details/<int:movie_id>/', views.movie_details, name='movie_details'),
    # path('get_movie_details/<int:movie_id>', views.get_movie_details, name = 'get_movie_details')
]
