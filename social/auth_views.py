"""
social/auth_views.py

Real authentication endpoints used by the login page (login.html):
  - password_login  : mobile number + password -> Django session login
  - request_otp      : mobile number -> emails a 6-digit one-time code
                        (flags needs_signup=True if the number is unknown)
  - self_signup       : mobile + name + email -> creates a new account
                        and sends the first OTP
  - verify_otp        : mobile number + code -> Django session login

All endpoints are called via fetch() from login.html and return JSON.
"""

import json
import re

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .models import OTPCode, Profile

User = get_user_model()


def _get_user_by_phone(phone):
    try:
        profile = Profile.objects.select_related("user").get(phone=phone)
        return profile.user
    except Profile.DoesNotExist:
        return None


def _mask_email(email):
    try:
        name, domain = email.split("@", 1)
        if len(name) <= 2:
            masked = name[0] + "*"
        else:
            masked = name[0] + "*" * (len(name) - 2) + name[-1]
        return f"{masked}@{domain}"
    except ValueError:
        return email


def _parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"ok": False, "error": "Invalid request."}, status=400)


def _generate_username(phone):
    base = f"user{phone}"
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}{suffix}"
    return username


@require_POST
@csrf_protect
def password_login(request):
    data, error = _parse_json(request)
    if error:
        return error

    phone = (data.get("mobile") or "").strip()
    password = data.get("password") or ""

    user = _get_user_by_phone(phone)
    if user is None:
        return JsonResponse(
            {"ok": False, "error": "No account found with this mobile number."}, status=400
        )

    authenticated_user = authenticate(request, username=user.username, password=password)
    if authenticated_user is None:
        return JsonResponse(
            {"ok": False, "error": "Incorrect mobile number or password."}, status=400
        )

    login(request, authenticated_user)
    return JsonResponse({"ok": True, "redirect": "/social/"})


@require_POST
@csrf_protect
def request_otp(request):
    data, error = _parse_json(request)
    if error:
        return error

    phone = (data.get("mobile") or "").strip()
    if not re.match(r"^\d{10}$", phone):
        return JsonResponse({"ok": False, "error": "Enter a valid 10-digit mobile number."}, status=400)

    user = _get_user_by_phone(phone)
    if user is None:
        # Unknown number — tell the frontend to show the name/email
        # fields so the person can create an account instead.
        return JsonResponse(
            {
                "ok": False,
                "needs_signup": True,
                "error": "No account found. Enter your name and email to create one.",
            },
            status=404,
        )

    if not user.email:
        return JsonResponse(
            {"ok": False, "error": "This account has no email on file. Contact support."},
            status=400,
        )

    otp = OTPCode.generate_for_user(user)

    try:
        send_mail(
            subject="Your Ghidora Transport login code",
            message=(
                f"Your one-time login code is: {otp.code}\n\n"
                "This code expires in 10 minutes. If you didn't request this, "
                "you can safely ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        return JsonResponse(
            {"ok": False, "error": "Could not send the code. Please try again."}, status=500
        )

    return JsonResponse({"ok": True, "message": f"Code sent to {_mask_email(user.email)}"})


@require_POST
@csrf_protect
def self_signup(request):
    """
    Creates a brand-new account for someone who tried to log in with a
    mobile number that isn't registered yet, then emails them their
    first OTP so they can finish signing in immediately.
    """
    data, error = _parse_json(request)
    if error:
        return error

    phone = (data.get("mobile") or "").strip()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()

    if not re.match(r"^\d{10}$", phone):
        return JsonResponse({"ok": False, "error": "Enter a valid 10-digit mobile number."}, status=400)
    if not name:
        return JsonResponse({"ok": False, "error": "Please enter your name."}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "error": "Enter a valid email address."}, status=400)

    if Profile.objects.filter(phone=phone).exists():
        return JsonResponse(
            {"ok": False, "error": "An account with this mobile number already exists."}, status=400
        )
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse(
            {"ok": False, "error": "An account with this email already exists."}, status=400
        )

    username = _generate_username(phone)
    user = User.objects.create(username=username, email=email, first_name=name[:30])
    user.set_unusable_password()  # this account only ever logs in via OTP
    user.save()

    # Profile is auto-created by the post_save signal in social/signals.py —
    # fetch it and attach the phone number.
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.phone = phone
    profile.save(update_fields=["phone"])

    otp = OTPCode.generate_for_user(user)
    try:
        send_mail(
            subject="Welcome to Ghidora Transport — your login code",
            message=(
                f"Hi {name},\n\nYour Ghidora Transport account has been created.\n\n"
                f"Your one-time login code is: {otp.code}\n\n"
                "This code expires in 10 minutes."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        return JsonResponse(
            {"ok": False, "error": "Account created, but the code could not be sent. Try 'Resend code'."},
            status=500,
        )

    return JsonResponse({"ok": True, "message": f"Account created. Code sent to {_mask_email(email)}"})


@require_POST
@csrf_protect
def verify_otp(request):
    data, error = _parse_json(request)
    if error:
        return error

    phone = (data.get("mobile") or "").strip()
    code = (data.get("otp") or "").strip()

    user = _get_user_by_phone(phone)
    if user is None:
        return JsonResponse(
            {"ok": False, "error": "No account found with this mobile number."}, status=400
        )

    otp = (
        OTPCode.objects.filter(user=user, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        return JsonResponse({"ok": False, "error": "Incorrect code."}, status=400)
    if otp.is_expired():
        return JsonResponse(
            {"ok": False, "error": "This code has expired. Request a new one."}, status=400
        )

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)
    return JsonResponse({"ok": True, "redirect": "/social/"})