from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.http import HttpRequest


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for django-allauth to safely handle SocialApp queries.
    Prevents MultipleObjectsReturned exceptions and ensures the app has
    a valid Google Client ID and Secret.
    """

    def get_app(self, request: HttpRequest, provider=None, client_id=None):
        apps = self.list_apps(request, provider=provider, client_id=client_id)

        target_app = None
        if len(apps) > 1:
            visible_apps = [app for app in apps if not app.settings.get("hidden")]
            target_app = visible_apps[0] if visible_apps else apps[0]
        elif len(apps) == 1:
            target_app = apps[0]
        else:
            raise SocialApp.DoesNotExist()

        # Ensure the SocialApp always has the valid Google secret & client_id from settings.py
        google_cfg = settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {})
        expected_secret = google_cfg.get('secret')
        expected_client_id = google_cfg.get('client_id')

        if expected_secret and target_app.secret != expected_secret:
            target_app.secret = expected_secret
            if target_app.pk:
                SocialApp.objects.filter(pk=target_app.pk).update(secret=expected_secret)

        if expected_client_id and target_app.client_id != expected_client_id:
            target_app.client_id = expected_client_id
            if target_app.pk:
                SocialApp.objects.filter(pk=target_app.pk).update(client_id=expected_client_id)

        return target_app
