from django.apps import AppConfig


def sync_google_social_app(sender, **kwargs):
    # Auto-clean duplicate SocialApp database entries for google & sync credentials
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        from django.conf import settings

        google_cfg = settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {})
        secret = google_cfg.get('secret') or getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        client_id = google_cfg.get('client_id') or getattr(settings, 'GOOGLE_CLIENT_ID', '')

        google_apps = list(SocialApp.objects.filter(provider='google'))
        if len(google_apps) > 1:
            for app in google_apps[1:]:
                app.delete()
            print(f"[AutoClean] Successfully removed {len(google_apps) - 1} duplicate Google SocialApp entries.")

        current_site = None
        try:
            current_site = Site.objects.get(id=getattr(settings, 'SITE_ID', 1))
        except Exception:
            current_site = Site.objects.first()

        if google_apps:
            main_app = google_apps[0]
            changed = False
            if secret and main_app.secret != secret:
                main_app.secret = secret
                changed = True
            if client_id and main_app.client_id != client_id:
                main_app.client_id = client_id
                changed = True
            if changed:
                main_app.save()
            if current_site and not main_app.sites.filter(id=current_site.id).exists():
                main_app.sites.add(current_site)
        elif client_id and secret:
            main_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=client_id,
                secret=secret
            )
            if current_site:
                main_app.sites.add(current_site)
            print(f"[AutoClean] Created Google SocialApp with client_id: {client_id[:15]}...")
    except Exception as e:
        pass


class SocialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "social"

    def ready(self):
        import social.signals   # noqa: F401
        from django.db.models.signals import post_migrate
        post_migrate.connect(sync_google_social_app, sender=self)