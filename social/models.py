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
    note = models.CharField(max_length=60, blank=True, help_text="Short Instagram note bubble above avatar")
    website = models.URLField(max_length=200, blank=True)
    gender = models.CharField(max_length=20, blank=True, default="Male")



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
    location = models.CharField(max_length=150, blank=True)

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

    def is_saved_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.saved_by.filter(user=user).exists()


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
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} on post #{self.post_id}"

    @property
    def like_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")

    def __str__(self):
        return f"{self.user.username} likes comment #{self.comment_id}"


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


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="posts/%Y/%m/")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Media #{self.id} for post #{self.post_id}"

    def is_video(self):
        if not self.image:
            return False
        ext = self.image.name.split(".")[-1].lower()
        return ext in ["mp4", "mov", "webm", "ogg", "mkv", "avi"]


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    media = models.FileField(upload_to="stories/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Story #{self.id} by {self.user.username}"

    def is_video(self):
        if not self.media:
            return False
        ext = self.media.name.split(".")[-1].lower()
        return ext in ["mp4", "mov", "webm", "ogg", "mkv", "avi"]


class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("story", "user")

    def __str__(self):
        return f"{self.user.username} viewed story #{self.story_id}"


class Highlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="highlights")
    title = models.CharField(max_length=30)
    cover_image = models.FileField(upload_to="highlights/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Highlight '{self.title}' by {self.user.username}"


class HighlightItem(models.Model):
    highlight = models.ForeignKey(Highlight, on_delete=models.CASCADE, related_name="items")
    media = models.FileField(upload_to="highlights/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_video(self):
        if not self.media:
            return False
        ext = self.media.name.split(".")[-1].lower()
        return ext in ["mp4", "mov", "webm", "ogg", "mkv", "avi"]


class Reel(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reels")
    video = models.FileField(upload_to="reels/%Y/%m/")
    caption = models.CharField(max_length=500, blank=True)
    audio_title = models.CharField(max_length=100, default="Original audio")
    likes = models.ManyToManyField(User, related_name="liked_reels", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reel #{self.id} by {self.author.username}"

    def total_likes(self):
        return self.likes.count()




class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation #{self.pk}"

    def get_other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()


class DirectMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"DM #{self.pk} from {self.sender.username}"


# ============================================================
# 👥 FOLLOW SYSTEM
# ============================================================
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


# ============================================================
# 🔖 SAVED / BOOKMARKED POSTS
# ============================================================
class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved post #{self.post_id}"


# ============================================================
# 🔔 NOTIFICATIONS SYSTEM
# ============================================================
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("LIKE", "Liked your post"),
        ("COMMENT", "Commented on your post"),
        ("REPLY", "Replied to your comment"),
        ("FOLLOW", "Started following you"),
        ("STORY_REACTION", "Reacted to your story"),
        ("MESSAGE", "Sent you a message"),
    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    text = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.notification_type} from {self.sender.username}"


# ============================================================
# ⚡ STORY REACTIONS
# ============================================================
class StoryReaction(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story_reactions")
    reaction = models.CharField(max_length=10)  # e.g. '❤️', '🔥', '😂', '🚚', '👏'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to story #{self.story_id}"


# ============================================================
# 🛡️ CONTENT & ABUSE REPORTS
# ============================================================
class Report(models.Model):
    REPORT_REASONS = (
        ("SPAM", "Spam or scam"),
        ("HARASSMENT", "Harassment or bullying"),
        ("INAPPROPRIATE", "Inappropriate content"),
        ("FAKE", "Fake account or misinformation"),
        ("OTHER", "Other issue"),
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_filed")
    target_type = models.CharField(
        max_length=20,
        choices=(("POST", "Post"), ("USER", "User"), ("COMMENT", "Comment"), ("REEL", "Reel")),
    )
    target_id = models.PositiveIntegerField()
    reason = models.CharField(max_length=30, choices=REPORT_REASONS)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=(("PENDING", "Pending"), ("RESOLVED", "Resolved"), ("DISMISSED", "Dismissed")),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report #{self.id} by {self.reporter.username} on {self.target_type} #{self.target_id}"