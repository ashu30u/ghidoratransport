from django.contrib import admin

from .models import Comment, Like, Post, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_driver", "created_at")
    list_filter = ("is_driver",)
    search_fields = ("user__username", "user__email")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author", "content", "created_at")
    can_delete = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "content_preview", "like_count", "comment_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("author__username", "content")
    inlines = [CommentInline]

    def content_preview(self, obj):
        return obj.content[:60]

    content_preview.short_description = "Content"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "content", "created_at")
    search_fields = ("author__username", "content")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
