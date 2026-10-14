import os
import sys
import sqlite3

# Force UTF-8 stdout/stderr to avoid UnicodeEncodeError in non-UTF-8 terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
    django.setup()

    from django.conf import settings

    db_path = settings.DATABASES['default']['NAME']
    print(f"Connecting to SQLite database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check existing columns in booking_review
    try:
        cursor.execute("PRAGMA table_info(booking_review)")
        rows = cursor.fetchall()
        existing_cols = {col[1]: col for col in rows}
    except Exception as e:
        print(f"Notice: booking_review table check skipped: {e}")
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

    # Check if booking_id has NOT NULL constraint
    booking_col = existing_cols.get('booking_id')
    if booking_col and booking_col[3] == 1:
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
            print("[OK] Successfully updated booking_review table! booking_id is now NULLable.")
        except Exception as e:
            try:
                cursor.execute("ROLLBACK;")
            except Exception:
                pass
            print("Notice fixing table constraint:", e)

    try:
        cursor.execute("UPDATE booking_review SET is_approved = 1 WHERE is_approved IS NULL OR is_approved = 0")
        conn.commit()
    except Exception as e:
        print("Notice updating is_approved:", e)

    # 2. Ensure booking_giabookingrecord table and missing columns exist
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
                    print(f"[OK] Added missing column '{col_name}' to booking_giabookingrecord table.")
                except Exception as e:
                    print(f"Notice adding {col_name} to booking_giabookingrecord: {e}")
        conn.commit()
    except Exception as gia_e:
        print(f"Notice in booking_giabookingrecord migration: {gia_e}")

    try:
        conn.close()
    except Exception:
        pass

    print("[OK] Schema checks completed successfully.")

except Exception as main_e:
    print(f"Notice in auto_migrate: {main_e}")
