import sqlite3
import os

db_path = r"C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject\db.sqlite3"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pickupwala_hornsound (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(150) NOT NULL,
            audio_file VARCHAR(100) NOT NULL,
            is_active BOOL NOT NULL DEFAULT 1,
            "order" UNSIGNED INT NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("SUCCESS: Table pickupwala_hornsound created in db.sqlite3")
else:
    print("db.sqlite3 not found")
