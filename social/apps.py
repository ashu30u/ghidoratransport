from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "social"          # ← "ghidora_social_app" की जगह ये होना चाहिए

    def ready(self):
        import social.signals   # noqa: F401

        # Auto-clean duplicate SocialApp database entries for google & sync credentials
        try:
            from allauth.socialaccount.models import SocialApp
            from django.conf import settings
            google_cfg = settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {})
            secret = google_cfg.get('secret')
            client_id = google_cfg.get('client_id')

            google_apps = list(SocialApp.objects.filter(provider='google'))
            if len(google_apps) > 1:
                for app in google_apps[1:]:
                    app.delete()
                print(f"[AutoClean] Successfully removed {len(google_apps) - 1} duplicate Google SocialApp entries.")
            
            if google_apps:
                main_app = google_apps[0]
                if secret and main_app.secret != secret:
                    main_app.secret = secret
                    main_app.save()
                if client_id and main_app.client_id != client_id:
                    main_app.client_id = client_id
                    main_app.save()
        except Exception:
            pass