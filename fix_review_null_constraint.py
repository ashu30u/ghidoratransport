import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
print(f"Fixing NOT NULL constraint in database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("BEGIN TRANSACTION;")

    # Check columns of current booking_review
    cursor.execute("PRAGMA table_info(booking_review);")
    cols = [col[1] for col in cursor.fetchall()]

    # Create temporary table with NULLable booking_id
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

    # Copy data safely
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
    cursor.execute("ROLLBACK;")
    print("❌ Error fixing table constraint:", e)

finally:
    conn.close()
