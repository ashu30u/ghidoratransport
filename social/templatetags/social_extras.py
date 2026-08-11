from django import template

register = template.Library()


@register.filter
def is_liked_by(post, user):
    """Usage in a template: {{ post|is_liked_by:request.user }}"""
    return post.is_liked_by(user)
