from django.db import models


def song_audio_path(instance, filename):
    return f"pickupwala/songs/{filename}"


def song_cover_path(instance, filename):
    return f"pickupwala/covers/{filename}"


class Shayari(models.Model):
    """One line shown on the signage board above the player. Admin adds/edits these directly."""

    text = models.CharField(
        max_length=300,
        help_text="Trucker slogan / shayari line shown on the signage board, e.g. 'देखो मगर प्यार से'",
    )
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide without deleting")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Shayari"
        verbose_name_plural = "Shayaris"

    def __str__(self):
        return self.text[:60]


class Song(models.Model):
    """One playlist track. Admin uploads the audio file (and optional cover art) here."""

    title = models.CharField(max_length=150)
    artist = models.CharField(max_length=150)
    audio_file = models.FileField(upload_to=song_audio_path, help_text="mp3 / wav / m4a file")
    cover_image = models.ImageField(
        upload_to=song_cover_path,
        blank=True,
        null=True,
        help_text="Optional cassette/cover art. If left blank the player shows the default cassette icon.",
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Song length in seconds, used for the progress bar. Leave 0 and the player will fall back to the audio file's own length.",
    )
    trip_km = models.PositiveIntegerField(
        default=150,
        help_text="Distance shown on the road progress readout for this song (purely cosmetic, e.g. '150 km')",
    )
    is_active = models.BooleanField(default=True, help_text="Uncheck to remove from the live playlist without deleting")
    order = models.PositiveIntegerField(default=0, help_text="Playlist order, lower numbers play first")
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} — {self.artist}"


class ChaiMessage(models.Model):
    """Chai break popup message shown when customer clicks the Tea button. Admin edits this in /admin/."""

    title = models.CharField(
        max_length=150,
        default="Chai pe charcha! ☕",
        help_text="Title for Chai break popup, e.g. 'Chai pe charcha! ☕'",
    )
    message = models.CharField(
        max_length=300,
        default="Music baad mein, pehle chai!",
        help_text="Subtitle/message shown on Chai break popup, e.g. 'Music baad mein, pehle chai!'",
    )
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide without deleting")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Chai Break Message"
        verbose_name_plural = "Chai Break Messages"

    def __str__(self):
        return f"{self.title} — {self.message}"

