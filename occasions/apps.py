from django.apps import AppConfig


class OccasionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'occasions'

    def ready(self):
        from .scheduler import start_occasion_scheduler
        start_occasion_scheduler()
