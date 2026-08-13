from django.http import JsonResponse
from django.shortcuts import render

from .models import Shayari, Song


def player_page(request):
    """Renders the Pickupwala player. The playlist/shayari itself is loaded via JS from playlist_api,
    so this view stays simple — no need to touch it when the admin adds new songs."""
    return render(request, "pickupwala/player.html")


def playlist_api(request):
    """Returns everything currently active in the admin: songs + shayari lines.
    New songs/shayaris added in /admin/ show up here immediately, no deploy needed."""
    songs = Song.objects.filter(is_active=True).order_by("order", "id")
    tracks = [
        {
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "audio_url": s.audio_file.url if s.audio_file else "",
            "cover_url": s.cover_image.url if s.cover_image else "",
            "duration": s.duration_seconds or 200,
            "km": s.trip_km,
        }
        for s in songs
    ]

    shayari = list(
        Shayari.objects.filter(is_active=True).order_by("order", "id").values_list("text", flat=True)
    )

    return JsonResponse({"tracks": tracks, "shayari": shayari})
