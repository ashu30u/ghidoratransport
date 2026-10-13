#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _auto_fix_sqlite_columns():
    try:
        import sqlite3
        from pathlib import Path
        db_path = Path(__file__).resolve().parent / 'db.sqlite3'
        if not db_path.exists():
            return
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure booking_giabookingrecord table and email column exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_giabookingrecord (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id VARCHAR(30) UNIQUE NOT NULL,
            customer_name VARCHAR(100) NOT NULL DEFAULT 'Gia AI Customer',
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(254) NULL,
            pickup VARCHAR(200) NOT NULL,
            destination VARCHAR(200) NOT NULL,
            goods_type VARCHAR(200) NULL,
            weight_kg INTEGER NOT NULL DEFAULT 500,
            weight_display VARCHAR(50) NOT NULL DEFAULT '500 kg',
            distance_km INTEGER NOT NULL DEFAULT 50,
            vehicle_assigned VARCHAR(100) NOT NULL DEFAULT 'Mahindra Pickup',
            total_fare REAL NOT NULL DEFAULT 0.0,
            status VARCHAR(30) NOT NULL DEFAULT 'Confirmed',
            source VARCHAR(50) NOT NULL DEFAULT 'Gia AI Assistant',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("PRAGMA table_info(booking_giabookingrecord)")
        gia_cols = {col[1] for col in cursor.fetchall()}
        if 'email' not in gia_cols:
            try:
                cursor.execute("ALTER TABLE booking_giabookingrecord ADD COLUMN email VARCHAR(254) NULL")
                conn.commit()
            except Exception:
                pass

        # Ensure booking_review columns exist
        try:
            cursor.execute("PRAGMA table_info(booking_review)")
            review_cols = {col[1] for col in cursor.fetchall()}
            review_alters = [
                ("user_id", "ALTER TABLE booking_review ADD COLUMN user_id INTEGER REFERENCES auth_user(id)"),
                ("guest_name", "ALTER TABLE booking_review ADD COLUMN guest_name VARCHAR(100) NULL"),
                ("guest_email", "ALTER TABLE booking_review ADD COLUMN guest_email VARCHAR(254) NULL"),
                ("guest_phone", "ALTER TABLE booking_review ADD COLUMN guest_phone VARCHAR(15) NULL"),
                ("comment", "ALTER TABLE booking_review ADD COLUMN comment TEXT NULL"),
                ("service_used", "ALTER TABLE booking_review ADD COLUMN service_used VARCHAR(100) DEFAULT 'Full Truck Transport'"),
                ("photo", "ALTER TABLE booking_review ADD COLUMN photo VARCHAR(100) NULL"),
                ("is_approved", "ALTER TABLE booking_review ADD COLUMN is_approved BOOL DEFAULT 1"),
                ("is_verified", "ALTER TABLE booking_review ADD COLUMN is_verified BOOL DEFAULT 0"),
                ("ip_address", "ALTER TABLE booking_review ADD COLUMN ip_address CHAR(39) NULL"),
            ]
            for col_name, sql in review_alters:
                if col_name not in review_cols:
                    try:
                        cursor.execute(sql)
                    except Exception:
                        pass
            conn.commit()
        except Exception:
            pass

        conn.close()
    except Exception:
        pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
    _auto_fix_sqlite_columns()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
