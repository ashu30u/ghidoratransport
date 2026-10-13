from django.contrib import admin

from .models import (
    Comment,
    CommentLike,
    Follow,
    Like,
    Notification,
    Post,
    PostImage,
    Profile,
    Report,
    SavedPost,
    Story,
    StoryReaction,
    StoryView,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_driver", "created_at")
    list_filter = ("is_driver",)
    search_fields = ("user__username", "user__email")


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author", "content", "created_at")
    can_delete = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "content_preview", "location", "like_count", "comment_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("author__username", "content", "location")
    inlines = [PostImageInline, CommentInline]

    def content_preview(self, obj):
        return obj.content[:60]

    content_preview.short_description = "Content"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "parent", "content", "created_at")
    search_fields = ("author__username", "content")


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "created_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "sender", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("recipient__username", "sender__username", "text")


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "caption", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "caption")


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ("id", "story", "user", "viewed_at")


@admin.register(StoryReaction)
class StoryReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "story", "user", "reaction", "created_at")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "target_type", "target_id", "reason", "status", "created_at")
    list_filter = ("target_type", "reason", "status", "created_at")
    search_fields = ("reporter__username", "details")
    actions = ["mark_resolved", "mark_dismissed"]

    def mark_resolved(self, request, queryset):
        queryset.update(status="RESOLVED")
    mark_resolved.short_description = "Mark selected reports as RESOLVED"

    def mark_dismissed(self, request, queryset):
        queryset.update(status="DISMISSED")
    mark_dismissed.short_description = "Mark selected reports as DISMISSED"

