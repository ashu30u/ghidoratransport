import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.conf import settings

try:
    db_path = settings.DATABASES['default']['NAME']
    print(f"Connecting to SQLite database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns in booking_review
    try:
        cursor.execute("PRAGMA table_info(booking_review)")
        rows = cursor.fetchall()
        existing_cols = {col[1]: col for col in rows}
    except Exception as e:
        print(f"Notice: booking_review table check skipped/error: {e}")
        existing_cols = {}

    alter_statements = [
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

    for col_name, sql in alter_statements:
        if col_name not in existing_cols:
            try:
                cursor.execute(sql)
            except Exception as e:
                print(f"Notice adding {col_name}: {e}")

    try:
        conn.commit()
    except Exception:
        pass

    # Check if booking_id has NOT NULL constraint (notnull == 1)
    booking_col = existing_cols.get('booking_id')
    needs_table_recreation = False
    if booking_col and booking_col[3] == 1:
        needs_table_recreation = True

    # Recreate table if booking_id is NOT NULL
    if needs_table_recreation:
        print("Fixing booking_id NOT NULL constraint in booking_review table...")
        try:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("BEGIN TRANSACTION;")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking_review_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER NOT NULL DEFAULT 5,
                comment TEXT NULL,
                review TEXT NULL,
                service_used VARCHAR(100) DEFAULT 'Full Truck Transport',
                photo VARCHAR(100) NULL,
                is_approved BOOL DEFAULT 1,
                is_verified BOOL DEFAULT 0,
                ip_address CHAR(39) NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                booking_id INTEGER NULL REFERENCES booking_booking(id) ON DELETE SET NULL,
                user_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL,
                guest_name VARCHAR(100) NULL,
                guest_email VARCHAR(254) NULL,
                guest_phone VARCHAR(15) NULL
            );
            """)
            cursor.execute("""
            INSERT INTO booking_review_new (id, rating, comment, review, service_used, photo, is_approved, is_verified, ip_address, created_at, booking_id, user_id, guest_name, guest_email, guest_phone)
            SELECT id, rating, comment, review, service_used, photo, is_approved, is_verified, ip_address, created_at, booking_id, user_id, guest_name, guest_email, guest_phone
            FROM booking_review;
            """)
            cursor.execute("DROP TABLE booking_review;")
            cursor.execute("ALTER TABLE booking_review_new RENAME TO booking_review;")
            cursor.execute("COMMIT;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            print("✅ Successfully updated booking_review table! booking_id is now NULLable.")
        except Exception as e:
            try:
                cursor.execute("ROLLBACK;")
            except Exception:
                pass
            print("Notice fixing table constraint:", e)

    try:
        conn.close()
    except Exception:
        pass

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE booking_review SET is_approved = 1 WHERE is_approved IS NULL OR is_approved = 0")
        conn.commit()
        conn.close()
    except Exception as e:
        print("Notice updating is_approved:", e)

    print("✅ booking_review table schema check completed.")

    # Ensure booking_giabookingrecord table and missing columns (email, etc.) exist
    try:
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
        conn.commit()

        cursor.execute("PRAGMA table_info(booking_giabookingrecord)")
        gia_rows = cursor.fetchall()
        gia_cols = {col[1] for col in gia_rows}
        
        gia_alter_statements = [
            ("email", "ALTER TABLE booking_giabookingrecord ADD COLUMN email VARCHAR(254) NULL"),
            ("customer_name", "ALTER TABLE booking_giabookingrecord ADD COLUMN customer_name VARCHAR(100) DEFAULT 'Gia AI Customer'"),
            ("goods_type", "ALTER TABLE booking_giabookingrecord ADD COLUMN goods_type VARCHAR(200) NULL"),
            ("weight_kg", "ALTER TABLE booking_giabookingrecord ADD COLUMN weight_kg INTEGER DEFAULT 500"),
            ("weight_display", "ALTER TABLE booking_giabookingrecord ADD COLUMN weight_display VARCHAR(50) DEFAULT '500 kg'"),
            ("distance_km", "ALTER TABLE booking_giabookingrecord ADD COLUMN distance_km INTEGER DEFAULT 50"),
            ("vehicle_assigned", "ALTER TABLE booking_giabookingrecord ADD COLUMN vehicle_assigned VARCHAR(100) DEFAULT 'Mahindra Pickup'"),
            ("total_fare", "ALTER TABLE booking_giabookingrecord ADD COLUMN total_fare REAL DEFAULT 0.0"),
            ("status", "ALTER TABLE booking_giabookingrecord ADD COLUMN status VARCHAR(30) DEFAULT 'Confirmed'"),
            ("source", "ALTER TABLE booking_giabookingrecord ADD COLUMN source VARCHAR(50) DEFAULT 'Gia AI Assistant'"),
        ]

        for col_name, sql in gia_alter_statements:
            if col_name not in gia_cols:
                try:
                    cursor.execute(sql)
                    print(f"✅ Added missing column '{col_name}' to booking_giabookingrecord table.")
                except Exception as e:
                    print(f"Notice adding {col_name} to booking_giabookingrecord: {e}")
        conn.commit()
        print("✅ booking_giabookingrecord table schema check completed.")
    except Exception as gia_e:
        print(f"Notice in booking_giabookingrecord migration: {gia_e}")

except Exception as main_e:
    print(f"Notice in auto_migrate: {main_e}")


def ensure_google_social_app():
    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp
        
        # 1. Live Production Site (ID 1)
        live_site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'ghidoratransport.onrender.com', 'name': 'Ghidora Transport (Live)'})
        live_site.domain = 'ghidoratransport.onrender.com'
        live_site.name = 'Ghidora Transport (Live)'
        live_site.save()

        # 2. Local Development Site (ID 2)
        local_site, _ = Site.objects.get_or_create(id=2, defaults={'domain': '127.0.0.1:8000', 'name': 'Ghidora Transport (Local)'})
        local_site.domain = '127.0.0.1:8000'
        local_site.name = 'Ghidora Transport (Local)'
        local_site.save()

        client_id = '520482080238-ejsi630q0nv6na0de3if97ug73f5rmmt.apps.googleusercontent.com'

        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google Login',
                'client_id': client_id,
                'secret': 'GOCSPX-dummy_secret',
            }
        )
        app.client_id = client_id
        app.sites.add(live_site, local_site)
        app.save()
        print(f"✅ Google SocialApp configured for Live ({live_site.domain}) and Local ({local_site.domain})")
    except Exception as e:
        print("❌ Error ensuring Google SocialApp:", e)

ensure_google_social_app()
