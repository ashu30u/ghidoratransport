import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def is_liked_by(post, user):
    """Usage in a template: {{ post|is_liked_by:request.user }}"""
    if not user or not user.is_authenticated:
        return False
    return post.is_liked_by(user)


@register.filter
def is_saved_by(post, user):
    """Usage in a template: {{ post|is_saved_by:request.user }}"""
    if not user or not user.is_authenticated:
        return False
    return post.is_saved_by(user)


@register.filter
def is_comment_liked_by(comment, user):
    """Usage in a template: {{ comment|is_comment_liked_by:request.user }}"""
    if not user or not user.is_authenticated:
        return False
    return comment.is_liked_by(user)


@register.filter
def is_following(user, target_user):
    """Usage: {{ request.user|is_following:profile_user }}"""
    if not user or not user.is_authenticated or not target_user:
        return False
    from social.models import Follow
    return Follow.objects.filter(follower=user, following=target_user).exists()


@register.filter
def get_initials(user):
    """Returns 1-2 letter initials for user avatar fallback"""
    if not user:
        return "U"
    full_name = user.get_full_name() if hasattr(user, "get_full_name") else ""
    if full_name and full_name.strip():
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return parts[0][0].upper()
    username = getattr(user, "username", str(user))
    return username[0].upper() if username else "U"


@register.filter(is_safe=True)
def format_social_text(value):
    """
    Escapes text for safety and parses #hashtags and @mentions into clickable links.
    """
    if not value:
        return ""
    safe_text = escape(value)

    # 1. Replace #hashtags with link to explore
    safe_text = re.sub(
        r"#(\w+)",
        r'<a href="/social/explore/?tag=\1" class="ig-hashtag-link">#\1</a>',
        safe_text,
    )

    # 2. Replace @mentions with link to user profile
    safe_text = re.sub(
        r"@(\w+)",
        r'<a href="/social/profile/\1/" class="ig-mention-link">@\1</a>',
        safe_text,
    )

    return mark_safe(safe_text)

