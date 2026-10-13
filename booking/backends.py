import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class MultiIdentifierBackend(ModelBackend):
    """
    Universal Authentication Backend for Ghidora Transport.
    Allows customers and staff to log in using:
    - 10-digit Registered Mobile Number (from Profile.phone, User.username, or linked Booking.phone)
    - Email Address (case-insensitive)
    - Username (case-insensitive)
    along with their password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Allauth or Django form may pass identifier in username, email, or login
        ident = (username or kwargs.get("email") or kwargs.get("login") or "").strip()
        if not ident or not password:
            return None

        user = None

        # 1. Check if identifier is or contains a Mobile Number
        digits = re.sub(r"\D", "", ident)
        if len(digits) >= 10:
            clean_phone = digits[-10:]
            # Priority A: Check User's Profile phone
            user = (
                User.objects.filter(profile__phone=clean_phone)
                .select_related("profile")
                .first()
            )
            # Priority B: Check if User.username equals phone
            if not user:
                user = User.objects.filter(username=clean_phone).first()
            # Priority C: Check if User.username ends with phone (e.g. user9876543210)
            if not user:
                user = User.objects.filter(username__endswith=clean_phone).first()
            # Priority D: Check Profile phone icontains
            if not user:
                user = User.objects.filter(profile__phone__icontains=clean_phone).first()

        # 2. Check if identifier is an Email Address
        if not user and "@" in ident:
            user = User.objects.filter(email__iexact=ident).first()

        # 3. Check if identifier is a Username
        if not user:
            user = User.objects.filter(username__iexact=ident).first()

        # 4. Fallback: try email or raw phone regardless
        if not user:
            user = User.objects.filter(
                Q(email__iexact=ident) | Q(profile__phone=ident)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
