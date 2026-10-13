from django.apps import AppConfig


class PickupwalaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pickupwala"
    verbose_name = "Pickupwala Radio"

    def ready(self):
        try:
            from .importer import auto_import_songs
            auto_import_songs()
        except Exception:
            pass


