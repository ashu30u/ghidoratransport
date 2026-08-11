import json
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileForm
from .models import Comment, Like, Post, Profile

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
    Main scrolling social feed page
    """
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Posted!")
            return redirect("social:feed")
    else:
        form = PostForm()

    posts_qs = Post.objects.select_related("author", "author__profile").prefetch_related(
        "likes", "comments"
    ).order_by("-created_at")
    
    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "social/feed.html",
        {"form": form, "page_obj": page_obj, "posts": page_obj.object_list},
    )


@login_required
def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("author", "author__profile"), pk=pk
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
    Toggles post likes via AJAX or standard form POST
    """
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "like_count": post.like_count})

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "social:feed"
    return redirect(next_url)


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("social:feed")
    return render(request, "social/confirm_delete.html", {"post": post})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    posts = Post.objects.filter(author=profile_user).select_related("author").order_by("-created_at")

    return render(
        request,
        "social/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "posts": posts,
            "post_count": posts.count(),
            "is_own_profile": request.user == profile_user,
        },
    )


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("social:profile", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "social/edit_profile.html", {"form": form})