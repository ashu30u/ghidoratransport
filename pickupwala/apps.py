from django.apps import AppConfig


class PickupwalaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pickupwala"
    verbose_name = "Pickupwala Radio"

    def ready(self):
        try:
            import os
            import sqlite3
            from django.conf import settings

            db_path = os.path.join(settings.BASE_DIR, "db.sqlite3")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS pickupwala_hornsound (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(150) NOT NULL,
                        audio_file VARCHAR(100) NOT NULL,
                        is_active BOOL NOT NULL DEFAULT 1,
                        "order" UNSIGNED INT NOT NULL DEFAULT 0
                    )
                """
                )
                conn.commit()
                conn.close()
        except Exception:
            pass

