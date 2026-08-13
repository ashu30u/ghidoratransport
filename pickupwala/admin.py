from django.contrib import admin
from django.utils.html import format_html

from .models import Shayari, Song, ChaiMessage


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "artist", "duration_display", "trip_km", "is_active", "audio_preview")
    list_display_links = ("title",)
    list_editable = ("order", "is_active")
    search_fields = ("title", "artist")
    list_filter = ("is_active",)
    fields = ("title", "artist", "audio_file", "cover_image", "duration_seconds", "trip_km", "is_active", "order")
    ordering = ("order", "id")

    def duration_display(self, obj):
        m, s = divmod(obj.duration_seconds or 0, 60)
        return f"{m}:{s:02d}"

    duration_display.short_description = "Duration"

    def audio_preview(self, obj):
        if obj.audio_file:
            return format_html('<audio controls style="height:28px;" src="{}"></audio>', obj.audio_file.url)
        return "-"

    audio_preview.short_description = "Preview"


@admin.register(Shayari)
class ShayariAdmin(admin.ModelAdmin):
    list_display = ("order", "text", "is_active")
    list_display_links = ("text",)
    list_editable = ("order", "is_active")
    search_fields = ("text",)
    list_filter = ("is_active",)
    ordering = ("order", "id")


@admin.register(ChaiMessage)
class ChaiMessageAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "message", "is_active")
    list_display_links = ("title",)
    list_editable = ("order", "is_active")
    search_fields = ("title", "message")
    list_filter = ("is_active",)
    ordering = ("order", "id")

