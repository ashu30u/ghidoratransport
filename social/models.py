import random
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    """
    One-to-one extension of Django's built-in User model.
    Created automatically for every user via the post_save signal
    in social/signals.py — you never create this manually.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # NEW: links a mobile number to this user, used by the password
    # and OTP login flows on the login page. Kept optional so existing
    # accounts (e.g. Google sign-ins) that don't set a phone still work.
    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        help_text="Used for mobile-number password login and OTP login",
    )

    # Lets the profile page (and later the follow/badge system) tell
    # customers apart from drivers without touching the User model.
    is_driver = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_absolute_url(self):
        return reverse("social:profile", kwargs={"username": self.user.username})


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to="posts/%Y/%m/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        preview = self.content[:40]
        return f"{self.author.username}: {preview}"

    def get_absolute_url(self):
        return reverse("social:post_detail", kwargs={"pk": self.pk})

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only like a given post once.
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user.username} likes post #{self.post_id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} on post #{self.post_id}"


# ============================================================
# NEW: Email OTP for mobile-number login
# ============================================================
class OTPCode(models.Model):
    """
    A single one-time login code sent to a user's email when they
    request OTP login using their mobile number. Codes expire after
    10 minutes and can only be used once.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @staticmethod
    def generate_for_user(user):
        code = f"{random.randint(0, 999999):06d}"
        return OTPCode.objects.create(user=user, code=code)

    def __str__(self):
        state = "used" if self.is_used else "active"
        return f"OTP for {self.user.username} ({state})"