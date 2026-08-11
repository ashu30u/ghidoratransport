from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "social"          # ← "ghidora_social_app" की जगह ये होना चाहिए

    def ready(self):
        import social.signals   # noqa: F401