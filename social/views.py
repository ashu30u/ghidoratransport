from datetime import timedelta
import json
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileForm, ReelForm, StoryForm
from .models import (
    Comment,
    CommentLike,
    Conversation,
    DirectMessage,
    Follow,
    Highlight,
    HighlightItem,
    Like,
    Notification,
    Post,
    PostImage,
    Profile,
    Reel,
    Report,
    SavedPost,
    Story,
    StoryReaction,
    StoryView,
)

User = get_user_model()

# Specify backend explicitly to support allauth + default model backend
AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'


# ================================================================
# 🔑 AUTHENTICATION VIEWS (for 3D login.html)
# ================================================================

@csrf_exempt
def password_login(request):
    """
    Handles Mobile & Password authentication from 3D login.html
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        mobile = data.get("mobile", "").strip()
        password = data.get("password", "")

        if not mobile or not password:
            return JsonResponse({"ok": False, "error": "Mobile number and password are required."})

        # Search user by username (mobile number) or email
        user = User.objects.filter(username=mobile).first()
        if not user:
            user = User.objects.filter(email=mobile).first()

        if user:
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user:
                login(request, auth_user, backend=AUTH_BACKEND)
                return JsonResponse({"ok": True, "redirect": "/"})

        return JsonResponse({"ok": False, "error": "Invalid mobile number or password."})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@csrf_exempt
def request_otp(request):
    """
    Generates and sends a 6-digit OTP to the user's email address
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        mobile = data.get("mobile", "").strip()

        if not mobile:
            return JsonResponse({"ok": False, "error": "Mobile number is required."})

        user = User.objects.filter(username=mobile).first()
        if not user:
            return JsonResponse({
                "ok": False,
                "needs_signup": True,
                "error": "No account found with this number. Please enter your name & email to sign up."
            })

        # Generate 6-digit OTP code
        otp = str(random.randint(100000, 999999))
        request.session["otp_code"] = otp
        request.session["otp_mobile"] = mobile

        # Email OTP dispatch
        if user.email:
            send_mail(
                "Ghidora Transport - Login OTP",
                f"Hello {user.first_name or user.username},\n\nYour 6-digit login OTP code for Ghidora Transport is: {otp}\n\nDo not share this code with anyone.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            return JsonResponse({"ok": True, "message": f"OTP code sent to your registered email ({user.email})."})
        else:
            return JsonResponse({"ok": True, "message": f"Demo OTP code: {otp}"})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@csrf_exempt
def self_signup(request):
    """
    Creates a new user account directly from the OTP modal flow
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        mobile = data.get("mobile", "").strip()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()

        if not mobile or not name or not email:
            return JsonResponse({"ok": False, "error": "Mobile, name, and email are all required."})

        if User.objects.filter(username=mobile).exists():
            return JsonResponse({"ok": False, "error": "An account with this mobile number already exists."})

        # Create new Django User
        user = User.objects.create_user(
            username=mobile,
            email=email,
            first_name=name
        )

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        request.session["otp_code"] = otp
        request.session["otp_mobile"] = mobile

        send_mail(
            "Ghidora Transport - Welcome & Verification OTP",
            f"Welcome to Ghidora Transport, {name}!\n\nYour verification OTP is: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

        return JsonResponse({"ok": True, "message": f"Account created! Verification OTP sent to {email}."})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@login_required
@csrf_exempt
def set_credentials(request):
    """
    Allows a customer logged in via Mobile / OTP / Google to set or update custom Username and Password
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_username = data.get("username", "").strip()
            new_password = data.get("password", "")

            user = request.user
            if new_username and new_username != user.username:
                if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                    return JsonResponse({"ok": False, "error": "Username already taken. Please choose another."})
                user.username = new_username

            if new_password:
                user.set_password(new_password)

            user.save()
            login(request, user, backend=AUTH_BACKEND)
            return JsonResponse({"ok": True, "message": "Username and password updated successfully! Next time you can log in with password."})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})

    return JsonResponse({"ok": False, "error": "POST method required."})


@csrf_exempt
def verify_otp(request):
    """
    Verifies the session OTP code and logs the user in
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        mobile = data.get("mobile", "").strip()
        otp = data.get("otp", "").strip()

        session_otp = request.session.get("otp_code")
        session_mobile = request.session.get("otp_mobile")

        if session_otp and str(session_otp) == str(otp) and session_mobile == mobile:
            user = User.objects.filter(username=mobile).first()
            if user:
                login(request, user, backend=AUTH_BACKEND)
                request.session.pop("otp_code", None)
                request.session.pop("otp_mobile", None)
                return JsonResponse({"ok": True, "redirect": "/"})

        return JsonResponse({"ok": False, "error": "Invalid or expired OTP code."})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


# ================================================================
# 📱 SOCIAL FEED & PROFILE VIEWS
# ================================================================

@login_required
def feed(request):
    """
    Main scrolling social feed page with Instagram UI and Stories
    """
    if request.method == "POST":
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            images = request.FILES.getlist("images")
            single_img = request.FILES.get("image")
            if single_img and not post.image:
                post.image = single_img
            elif images and not post.image:
                post.image = images[0]
            post.save()

            if images:
                for idx, img in enumerate(images):
                    PostImage.objects.create(post=post, image=img, order=idx)
            elif single_img:
                PostImage.objects.create(post=post, image=single_img, order=0)

            if is_ajax:
                return JsonResponse({"ok": True, "message": "Posted successfully!", "redirect": reverse("social:feed")})
            messages.success(request, "Posted!")
            return redirect("social:feed")
        else:
            if is_ajax:
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    else:
        form = PostForm()

    # Active Stories (created in the last 24 hours)
    cutoff = timezone.now() - timedelta(hours=24)
    active_stories = (
        Story.objects.filter(created_at__gte=cutoff)
        .select_related("user", "user__profile")
        .prefetch_related("views")
        .order_by("created_at")
    )

    # Group stories by user
    user_stories_map = {}
    for story in active_stories:
        u = story.user
        if u.id not in user_stories_map:
            avatar_url = u.profile.avatar.url if (hasattr(u, "profile") and u.profile.avatar) else None
            user_stories_map[u.id] = {
                "user": u,
                "username": u.username,
                "display_name": u.get_full_name() or u.username,
                "avatar_url": avatar_url,
                "is_driver": getattr(u.profile, "is_driver", False) if hasattr(u, "profile") else False,
                "stories": [],
                "has_unseen": False,
            }

        viewed = story.views.filter(user=request.user).exists()
        if not viewed:
            user_stories_map[u.id]["has_unseen"] = True

        user_stories_map[u.id]["stories"].append({
            "id": story.id,
            "media_url": story.media.url,
            "caption": story.caption,
            "created_at": story.created_at.strftime("%I:%M %p"),
            "viewed": viewed,
        })

    # Logged-in user's story status
    my_story_group = user_stories_map.pop(request.user.id, None)
    other_story_groups = list(user_stories_map.values())

    posts_qs = (
        Post.objects.select_related("author", "author__profile")
        .prefetch_related("images", "likes", "likes__user", "comments", "comments__author", "comments__author__profile")
        .order_by("-created_at")
    )

    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    story_form = StoryForm()
    suggested_users = User.objects.exclude(id=request.user.id).select_related("profile")[:5]

    reels_qs = (
        Reel.objects.select_related("author", "author__profile")
        .prefetch_related("likes")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "social/feed.html",
        {
            "form": form,
            "story_form": story_form,
            "page_obj": page_obj,
            "posts": page_obj.object_list,
            "my_story_group": my_story_group,
            "other_story_groups": other_story_groups,
            "suggested_users": suggested_users,
            "reels": reels_qs,
        },
    )



@login_required
def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("author", "author__profile").prefetch_related("images"), pk=pk
    )
    comments = post.comments.select_related("author", "author__profile")

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("social:post_detail", pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(
        request,
        "social/post_detail.html",
        {"post": post, "comments": comments, "comment_form": comment_form},
    )


@login_required
@require_POST
def like_toggle(request, pk):
    """
    Toggles post likes via AJAX or standard form POST with real Notification
    """
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Trigger notification to post author
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type="LIKE",
                post=post,
                text="Liked your post",
            )

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.META.get("HTTP_ACCEPT") == "application/json":
        return JsonResponse({"liked": liked, "like_count": post.like_count})

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "social:feed"
    return redirect(next_url)


@login_required
@require_POST
def save_toggle(request, pk):
    """
    Toggles bookmark / saved state for a post
    """
    post = get_object_or_404(Post, pk=pk)
    saved_obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved_obj.delete()
        saved = False
    else:
        saved = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.META.get("HTTP_ACCEPT") == "application/json":
        return JsonResponse({"ok": True, "saved": saved})

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "social:feed"
    return redirect(next_url)


@login_required
def saved_posts(request):
    """
    Shows grid of posts saved/bookmarked by the logged-in user
    """
    saved_records = (
        SavedPost.objects.filter(user=request.user)
        .select_related("post", "post__author", "post__author__profile")
        .prefetch_related("post__images")
        .order_by("-created_at")
    )
    posts = [s.post for s in saved_records]
    return render(request, "social/saved_posts.html", {"posts": posts})


@login_required
@require_POST
def add_comment_ajax(request, pk):
    """
    Adds a comment or reply via AJAX and generates real Notification
    """
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get("content", "").strip()
    parent_id = request.POST.get("parent_id")

    if not content:
        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
            parent_id = data.get("parent_id")
        except Exception:
            pass

    if not content:
        return JsonResponse({"ok": False, "error": "Comment cannot be empty."}, status=400)

    parent = None
    if parent_id:
        parent = Comment.objects.filter(pk=parent_id, post=post).first()

    comment = Comment.objects.create(post=post, author=request.user, parent=parent, content=content)

    # Generate Notification
    if parent and parent.author != request.user:
        Notification.objects.create(
            recipient=parent.author,
            sender=request.user,
            notification_type="REPLY",
            post=post,
            comment=comment,
            text=f"Replied: {content[:45]}",
        )
    elif post.author != request.user:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type="COMMENT",
            post=post,
            comment=comment,
            text=f"Commented: {content[:45]}",
        )

    avatar_url = request.user.profile.avatar.url if (hasattr(request.user, "profile") and request.user.profile.avatar) else None

    return JsonResponse({
        "ok": True,
        "comment": {
            "id": comment.id,
            "author": request.user.username,
            "display_name": request.user.get_full_name() or request.user.username,
            "avatar_url": avatar_url,
            "is_driver": getattr(request.user.profile, "is_driver", False) if hasattr(request.user, "profile") else False,
            "content": comment.content,
            "parent_id": parent.id if parent else None,
            "created_at": "Just now",
            "like_count": 0,
            "is_liked": False,
        },
        "comment_count": post.comment_count,
    })


@login_required
@require_POST
def reply_comment_ajax(request, pk):
    """
    Convenience alias for replying to comment #pk
    """
    parent_comment = get_object_or_404(Comment, pk=pk)
    return add_comment_ajax(request, parent_comment.post_id)


@login_required
@require_POST
def like_comment_ajax(request, pk):
    """
    Toggles like on a comment
    """
    comment = get_object_or_404(Comment, pk=pk)
    cl, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        cl.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({"ok": True, "liked": liked, "like_count": comment.like_count})


@login_required
@require_POST
def delete_comment_ajax(request, pk):
    """
    Deletes comment if author is comment owner or post owner
    """
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user and comment.post.author != request.user:
        return JsonResponse({"ok": False, "error": "Permission denied."}, status=403)

    comment.delete()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def share_post_dm(request, pk=None):
    """
    Shares a post into a 1-on-1 Direct Message with target username
    """
    post_id = pk or request.POST.get("post_id") or request.POST.get("pk")
    username = request.POST.get("recipient_username") or request.POST.get("username", "").strip()

    if not post_id or not username:
        if request.body:
            try:
                bdata = json.loads(request.body)
                post_id = post_id or bdata.get("post_id") or bdata.get("pk")
                username = username or bdata.get("recipient_username") or bdata.get("username", "").strip()
            except Exception:
                pass

    if not post_id:
        return JsonResponse({"ok": False, "error": "Post ID is required."}, status=400)
    if not username:
        return JsonResponse({"ok": False, "error": "Recipient username required."}, status=400)

    post = get_object_or_404(Post, pk=post_id)
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({"ok": False, "error": "Cannot share to yourself."}, status=400)

    # Find or create conversation
    conv = Conversation.objects.filter(participants=request.user).filter(participants=target_user).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, target_user)

    post_url = request.build_absolute_uri(reverse("social:post_detail", kwargs={"pk": post.pk}))
    msg_text = f"Shared post by @{post.author.username}:\n{post_url}"
    DirectMessage.objects.create(conversation=conv, sender=request.user, content=msg_text)
    conv.save()

    return JsonResponse({"ok": True, "message": f"Post shared with @{target_user.username}!"})


@login_required
def post_likes_list(request, pk):
    """
    Returns list of users who liked the post for modal display
    """
    post = get_object_or_404(Post, pk=pk)
    likes = post.likes.select_related("user", "user__profile").all()
    user_list = []
    for l in likes:
        u = l.user
        avatar_url = u.profile.avatar.url if (hasattr(u, "profile") and u.profile.avatar) else None
        user_list.append({
            "username": u.username,
            "display_name": u.get_full_name() or u.username,
            "avatar_url": avatar_url,
            "is_driver": getattr(u.profile, "is_driver", False) if hasattr(u, "profile") else False,
        })
    return JsonResponse({"ok": True, "likes": user_list, "count": len(user_list)})


@login_required
@require_POST
def create_story(request):
    """
    Uploads a new 24h story
    """
    form = StoryForm(request.POST, request.FILES)
    if form.is_valid():
        story = form.save(commit=False)
        story.user = request.user
        story.save()
        messages.success(request, "Story posted successfully!")
        return redirect("social:feed")
    else:
        messages.error(request, "Failed to upload story. Please choose a valid image.")
        return redirect("social:feed")


@login_required
@require_POST
def view_story_api(request, pk):
    """
    Marks a story as viewed by the logged-in user
    """
    story = get_object_or_404(Story, pk=pk)
    StoryView.objects.get_or_create(story=story, user=request.user)
    return JsonResponse({"ok": True})


@login_required
@require_POST
def react_story_api(request, pk):
    """
    Adds emoji reaction to a story and notifies story author
    """
    story = get_object_or_404(Story, pk=pk)
    reaction = request.POST.get("reaction", "❤️").strip()
    if not reaction and request.body:
        try:
            reaction = json.loads(request.body).get("reaction", "❤️").strip()
        except Exception:
            pass

    StoryReaction.objects.create(story=story, user=request.user, reaction=reaction)

    if story.user != request.user:
        Notification.objects.create(
            recipient=story.user,
            sender=request.user,
            notification_type="STORY_REACTION",
            story=story,
            text=f"Reacted {reaction} to your story",
        )

    return JsonResponse({"ok": True, "reaction": reaction})


@login_required
def story_viewers_api(request, pk):
    """
    Returns list of viewers and their reactions for the story owner
    """
    story = get_object_or_404(Story, pk=pk, user=request.user)
    views = story.views.select_related("user", "user__profile").all()
    reactions = {r.user_id: r.reaction for r in story.reactions.all()}

    viewers = []
    for v in views:
        u = v.user
        avatar_url = u.profile.avatar.url if (hasattr(u, "profile") and u.profile.avatar) else None
        viewers.append({
            "username": u.username,
            "display_name": u.get_full_name() or u.username,
            "avatar_url": avatar_url,
            "reaction": reactions.get(u.id),
            "viewed_at": v.viewed_at.strftime("%I:%M %p"),
        })

    return JsonResponse({"ok": True, "count": len(viewers), "viewers": viewers})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("social:feed")

    return render(request, "social/confirm_delete.html", {"post": post})


@login_required
@require_POST
def create_highlight(request):
    """
    Creates a new Story Highlight for user profile (supporting photo or video)
    """
    title = request.POST.get("title", "").strip() or "Highlight"
    media = request.FILES.get("media") or request.FILES.get("cover_image")

    if not media:
        messages.error(request, "Please select a photo or video for your Highlight.")
        return redirect("social:profile", username=request.user.username)

    highlight = Highlight.objects.create(
        user=request.user,
        title=title,
        cover_image=media,
    )

    HighlightItem.objects.create(
        highlight=highlight,
        media=media,
        caption=request.POST.get("caption", "").strip(),
    )

    messages.success(request, f"Highlight '{title}' created successfully!")
    return redirect("social:profile", username=request.user.username)


@login_required
def reels_feed(request):
    """
    Instagram Reels Full-Screen Feed
    """
    reels = Reel.objects.select_related("author", "author__profile").prefetch_related("likes").order_by("-created_at")
    reel_form = ReelForm()
    return render(request, "social/reels.html", {"reels": reels, "reel_form": reel_form})


@login_required
def create_reel(request):
    """
    Creates and posts a new Reel
    """
    if request.method == "POST":
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.author = request.user
            reel.save()
            messages.success(request, "Reel posted successfully!")
        else:
            messages.error(request, "Failed to upload Reel. Please select a valid video file.")
        return redirect(request.META.get("HTTP_REFERER") or "social:reels_feed")
    return redirect("social:reels_feed")


@login_required
@require_POST
def like_reel_api(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    if request.user in reel.likes.all():
        reel.likes.remove(request.user)
        liked = False
    else:
        reel.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "total_likes": reel.total_likes()})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    posts = (
        Post.objects.filter(author=profile_user)
        .select_related("author")
        .prefetch_related("images", "likes", "comments")
        .order_by("-created_at")
    )
    highlights = Highlight.objects.filter(user=profile_user).prefetch_related("items")
    reels = Reel.objects.filter(author=profile_user).select_related("author").order_by("-created_at")

    is_own = request.user == profile_user
    follower_count = profile_user.followers_set.count()
    following_count = profile_user.following_set.count()
    is_following = False if is_own else Follow.objects.filter(follower=request.user, following=profile_user).exists()

    saved_posts = []
    if is_own:
        saved_records = (
            SavedPost.objects.filter(user=request.user)
            .select_related("post", "post__author")
            .prefetch_related("post__images")
            .order_by("-created_at")
        )
        saved_posts = [s.post for s in saved_records]

    return render(
        request,
        "social/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "posts": posts,
            "follower_count": follower_count,
            "followers_count": follower_count,
            "following_count": following_count,
            "is_following": is_following,
            "is_own_profile": is_own,
            "highlights": highlights,
            "reels": reels,
            "reel_count": reels.count(),
            "saved_posts": saved_posts,
            "saved_count": len(saved_posts) if is_own else 0,
        },
    )


# ================================================================
# 👥 FOLLOW / UNFOLLOW SYSTEM
# ================================================================

@login_required
@require_POST
def follow_toggle(request, username):
    """
    Follows or unfollows target user and returns updated counts
    """
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({"ok": False, "error": "You cannot follow yourself."}, status=400)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type="FOLLOW",
            text="Started following you",
        )

    return JsonResponse({
        "ok": True,
        "following": following,
        "follower_count": target_user.followers_set.count(),
        "following_count": target_user.following_set.count(),
    })


@login_required
def followers_list(request, username):
    """
    Returns list of followers for modal display
    """
    target_user = get_object_or_404(User, username=username)
    followers = target_user.followers_set.select_related("follower", "follower__profile").all()
    user_list = []
    for f in followers:
        u = f.follower
        avatar_url = u.profile.avatar.url if (hasattr(u, "profile") and u.profile.avatar) else None
        is_following_them = False
        if request.user.is_authenticated and request.user != u:
            is_following_them = Follow.objects.filter(follower=request.user, following=u).exists()
        user_list.append({
            "username": u.username,
            "display_name": u.get_full_name() or u.username,
            "avatar_url": avatar_url,
            "is_driver": getattr(u.profile, "is_driver", False) if hasattr(u, "profile") else False,
            "is_following": is_following_them,
            "is_me": u == request.user,
        })
    return JsonResponse({"ok": True, "users": user_list, "followers": user_list, "count": len(user_list)})


@login_required
def following_list(request, username):
    """
    Returns list of users that target_user is following
    """
    target_user = get_object_or_404(User, username=username)
    following_qs = target_user.following_set.select_related("following", "following__profile").all()
    user_list = []
    for f in following_qs:
        u = f.following
        avatar_url = u.profile.avatar.url if (hasattr(u, "profile") and u.profile.avatar) else None
        is_following_them = False
        if request.user.is_authenticated and request.user != u:
            is_following_them = Follow.objects.filter(follower=request.user, following=u).exists()
        user_list.append({
            "username": u.username,
            "display_name": u.get_full_name() or u.username,
            "avatar_url": avatar_url,
            "is_driver": getattr(u.profile, "is_driver", False) if hasattr(u, "profile") else False,
            "is_following": is_following_them,
            "is_me": u == request.user,
        })
    return JsonResponse({"ok": True, "users": user_list, "following": user_list, "count": len(user_list)})


# ================================================================
# 🔔 NOTIFICATIONS SYSTEM
# ================================================================

@login_required
def notifications_list_api(request):
    """
    Returns real notifications for logged-in user
    """
    notifs = (
        request.user.notifications.select_related("sender", "sender__profile", "post", "comment", "story")
        .all()[:40]
    )
    data = []
    for n in notifs:
        sender_avatar = n.sender.profile.avatar.url if (hasattr(n.sender, "profile") and n.sender.profile.avatar) else None
        post_thumb = None
        target_url = None
        if n.post:
            target_url = reverse("social:post_detail", kwargs={"pk": n.post.id})
            if n.post.image:
                post_thumb = n.post.image.url
            elif n.post.images.first():
                post_thumb = n.post.images.first().image.url
        elif n.notification_type == "FOLLOW":
            target_url = reverse("social:profile", kwargs={"username": n.sender.username})
        elif n.story:
            target_url = reverse("social:feed")

        data.append({
            "id": n.id,
            "sender_username": n.sender.username,
            "sender_avatar": sender_avatar,
            "type": n.notification_type,
            "text": n.text or n.get_notification_type_display(),
            "target_url": target_url,
            "post_thumb": post_thumb,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%d %b, %I:%M %p"),
        })

    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"ok": True, "notifications": data, "unread_count": unread_count})


@login_required
@require_POST
def mark_notifications_read(request):
    """
    Marks all notifications for user as read
    """
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({"ok": True})


# ================================================================
# 🔍 SEARCH & DISCOVERY API
# ================================================================

@login_required
def search_api(request):
    """
    Real-time debounced AJAX search across users and posts/tags
    """
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"ok": True, "users": [], "posts": []})

    clean_q = q.lstrip("#").lstrip("@")

    # 1. Search Users
    users_qs = User.objects.filter(
        Q(username__icontains=clean_q) |
        Q(first_name__icontains=clean_q) |
        Q(last_name__icontains=clean_q)
    ).select_related("profile").distinct()[:10]

    users_data = []
    for u in users_qs:
        avatar_url = u.profile.avatar.url if (hasattr(u, "profile") and u.profile.avatar) else None
        users_data.append({
            "username": u.username,
            "display_name": u.get_full_name() or u.username,
            "avatar_url": avatar_url,
            "is_driver": getattr(u.profile, "is_driver", False) if hasattr(u, "profile") else False,
            "profile_url": reverse("social:profile", kwargs={"username": u.username}),
        })

    # 2. Search Posts (by caption or location)
    posts_qs = Post.objects.filter(
        Q(content__icontains=q) |
        Q(content__icontains=f"#{clean_q}") |
        Q(location__icontains=clean_q)
    ).select_related("author").distinct()[:8]

    posts_data = []
    for p in posts_qs:
        thumb = p.image.url if p.image else (p.images.first().image.url if p.images.first() else None)
        posts_data.append({
            "id": p.id,
            "author": p.author.username,
            "snippet": p.content[:60],
            "location": p.location,
            "thumb": thumb,
            "url": reverse("social:post_detail", kwargs={"pk": p.id}),
        })

    # 3. Extract matching hashtags
    import re
    hashtag_set = set()
    for p in posts_qs:
        for tag in re.findall(r"#(\w+)", p.content):
            if clean_q.lower() in tag.lower():
                hashtag_set.add(tag)

    hashtags_data = [{"tag": tag, "count": Post.objects.filter(content__icontains=f"#{tag}").count()} for tag in list(hashtag_set)[:6]]

    return JsonResponse({
        "ok": True,
        "users": users_data,
        "posts": posts_data,
        "hashtags": hashtags_data,
    })


# ================================================================
# 🛡️ CONTENT REPORTING
# ================================================================

@login_required
@require_POST
def submit_report_api(request):
    """
    Submits a user, post, comment, or reel report for admin moderation
    """
    try:
        data = request.POST
        if not data and request.body:
            data = json.loads(request.body)

        target_type = data.get("target_type", "POST").upper()
        target_id = int(data.get("target_id", 0))
        reason = data.get("reason", "OTHER").upper()
        details = data.get("details", "").strip()

        Report.objects.create(
            reporter=request.user,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            details=details,
        )
        return JsonResponse({"ok": True, "message": "Thank you. Your report has been submitted for review."})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)




@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"

    if request.method == "POST":
        if request.POST.get("remove_avatar") == "1":
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None
                profile.save()
            if is_ajax:
                return JsonResponse({"ok": True, "message": "Profile photo removed."})
            messages.success(request, "Profile photo removed.")
            return redirect("social:edit_profile")

        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.refresh_from_db()
            if is_ajax:
                return JsonResponse({
                    "ok": True,
                    "message": "Profile updated successfully.",
                    "username": request.user.username,
                    "full_name": request.user.get_full_name() or request.user.username,
                    "bio": profile.bio,
                    "redirect_url": reverse("social:profile", kwargs={"username": request.user.username})
                })
            messages.success(request, "Profile updated successfully.")
            return redirect("social:profile", username=request.user.username)
        else:
            if is_ajax:
                errors_dict = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
                return JsonResponse({"ok": False, "errors": errors_dict}, status=400)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "social/edit_profile.html", {"form": form, "profile": profile})



@login_required
def explore(request):
    """
    Instagram-style Explore grid showing all users' posts, most recent first.
    """
    posts_qs = (
        Post.objects.select_related("author", "author__profile")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    paginator = Paginator(posts_qs, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "social/explore.html",
        {
            "posts": page_obj.object_list,
            "page_obj": page_obj,
        },
    )



@login_required
def inbox(request):
    """
    Lists the logged-in user's conversations, ordered by updated_at desc.
    """
    conversations = (
        request.user.conversations
        .prefetch_related("participants", "participants__profile", "messages", "messages__sender")
        .order_by("-updated_at")
    )

    items = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        if not other_user:
            continue
        last_message = conv.messages.last()
        has_unread = False
        if last_message and not last_message.is_read and last_message.sender != request.user:
            has_unread = True

        items.append({
            "conversation": conv,
            "other_user": other_user,
            "last_message": last_message,
            "has_unread": has_unread,
        })

    return render(
        request,
        "social/inbox.html",
        {
            "conversation_items": items,
        },
    )


@login_required
def conversation_detail(request, pk):
    """
    Shows message thread for a single conversation and handles message sending.
    Auto-marks unread messages as read.
    """
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related("participants", "participants__profile", "messages", "messages__sender"),
        pk=pk,
        participants=request.user,
    )

    other_user = conversation.get_other_participant(request.user)

    # Handle POST message submission (regular form submit fallback)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            DirectMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
            )
            conversation.save()  # update updated_at
            return redirect("social:conversation_detail", pk=conversation.pk)

    # Mark unread messages sent by other user as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages_list = conversation.messages.all().select_related("sender", "sender__profile")

    return render(
        request,
        "social/conversation_detail.html",
        {
            "conversation": conversation,
            "other_user": other_user,
            "chat_messages": messages_list,
        },
    )


@login_required
def start_conversation(request, username):
    """
    Gets or creates a 1-on-1 conversation with target username and redirects to detail.
    """
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        messages.warning(request, "You cannot message yourself.")
        return redirect("social:inbox")

    # Find existing conversation between the two users
    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=target_user)
        .first()
    )

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, target_user)

    return redirect("social:conversation_detail", pk=conversation.pk)


@login_required
@csrf_exempt
def send_message_ajax(request, pk):
    """
    AJAX endpoint to send or fetch new messages in a conversation.
    """
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)

    if request.method == "POST":
        try:
            content = request.POST.get("content", "").strip()
            if not content and request.body:
                data = json.loads(request.body)
                content = data.get("content", "").strip()

            if not content:
                return JsonResponse({"ok": False, "error": "Message content cannot be empty."})

            msg = DirectMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
            )
            conversation.save()

            return JsonResponse({
                "ok": True,
                "message": {
                    "id": msg.id,
                    "sender": msg.sender.username,
                    "content": msg.content,
                    "created_at": msg.created_at.strftime("%I:%M %p"),
                    "is_mine": True,
                }
            })
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})

    # GET request returns latest messages (polling support)
    after_id = request.GET.get("after_id", 0)
    new_msgs = conversation.messages.filter(id__gt=after_id).select_related("sender")
    
    # Mark incoming messages as read
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    data = [
        {
            "id": m.id,
            "sender": m.sender.username,
            "content": m.content,
            "created_at": m.created_at.strftime("%I:%M %p"),
            "is_mine": m.sender == request.user,
        }
        for m in new_msgs
    ]

    return JsonResponse({"ok": True, "messages": data})