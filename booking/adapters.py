from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse


class RoleBasedAccountAdapter(DefaultAccountAdapter):
    """
    Custom Account Adapter for Ghidora Transport.
    Handles role-based redirection after login/signup:
    - Admin / Staff / Superuser -> Redirects to Main Website ('/')
    - Normal Customer -> Redirects to User Dashboard ('/user-dashboard/')
    - Logout -> Redirects to Main Website ('/')
    """

    def get_login_redirect_url(self, request):
        user = request.user
        # If user is staff or superuser, direct to main public website
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return '/'
        # Normal authenticated customers go to their dedicated User Dashboard
        return '/user-dashboard/'

    def get_logout_redirect_url(self, request):
        return '/'

    def get_signup_redirect_url(self, request):
        return '/user-dashboard/'
