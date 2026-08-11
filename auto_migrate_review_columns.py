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
existing_cols = [col[1] for col in cursor.fetchall()]
print(f"Existing columns in booking_review: {existing_cols}")

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
conn.close()

# Update is_approved to 1 for all existing reviews
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("UPDATE booking_review SET is_approved = 1 WHERE is_approved IS NULL OR is_approved = 0")
conn.commit()
conn.close()

print("✅ booking_review table schema updated successfully!")
