from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('game/<int:game_id>/add/', views.add_game_to_backlog, name='add_game_to_backlog'),
    path('profile/', views.profile, name='profile'),
    path('profile/terminados/', views.profile_terminados, name='profile_terminados'),
    path('profile/jugando/', views.profile_jugando, name='profile_jugando'),
    path('profile/abandonados/', views.profile_abandonados, name='profile_abandonados'),
    path('profile/pendientes/', views.profile_pendientes, name='profile_pendientes'),
    path('api/search/', views.search_games, name='search_games'),
]
