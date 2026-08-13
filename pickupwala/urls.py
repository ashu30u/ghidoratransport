from django.urls import path

from . import views

app_name = "pickupwala"

urlpatterns = [
    path("", views.player_page, name="player"),
    path("api/playlist/", views.playlist_api, name="playlist-api"),
]
