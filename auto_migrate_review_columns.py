import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
print(f"Connecting to SQLite database at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns in booking_review
cursor.execute("PRAGMA table_info(booking_review)")
rows = cursor.fetchall()
existing_cols = {col[1]: col for col in rows}
print(f"Existing columns in booking_review: {list(existing_cols.keys())}")

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
            print(f"Adding column '{col_name}' to booking_review...")
            cursor.execute(sql)
        except Exception as e:
            print(f"Error adding {col_name}: {e}")

conn.commit()

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
        cursor.execute("ROLLBACK;")
        print("❌ Error fixing table constraint:", e)

conn.close()

# Update is_approved to 1 for all existing reviews
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("UPDATE booking_review SET is_approved = 1 WHERE is_approved IS NULL OR is_approved = 0")
    conn.commit()
except Exception as e:
    print("Error updating is_approved:", e)
conn.close()

print("✅ booking_review table schema updated successfully!")
