import os
import sqlite3
from django.apps import AppConfig


class BookingConfig(AppConfig):
    name = 'booking'

    def ready(self):
        try:
            from django.conf import settings
            db_path = settings.DATABASES['default']['NAME']
            if db_path and os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(booking_booking)")
                cols = [col[1] for col in cursor.fetchall()]
                if cols and 'payment_status' not in cols:
                    cursor.execute("ALTER TABLE booking_booking ADD COLUMN payment_status VARCHAR(30) DEFAULT 'Pending'")
                    conn.commit()
                conn.close()
        except Exception:
            pass
