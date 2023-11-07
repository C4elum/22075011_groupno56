from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('select-genres/', views.select_genres, name='select_genres'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('profile/', views.user_profile, name='user_profile'),
    path('logout/', views.user_logout, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('move-to-watched/', views.move_to_watched, name='move_to_watched'),
]