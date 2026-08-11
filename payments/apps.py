from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
    verbose_name = "Ghidora Payment Management"

    def ready(self):
        # Connect signal handlers (notifications, audit logs, etc.)
        import payments.signals  # noqa: F401
