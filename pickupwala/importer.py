import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from django.conf import settings

# List of known singers for accurate artist extraction
KNOWN_SINGERS = [
    "Kumar Sanu", "Alka Yagnik", "Udit Narayan", "Jagjit Singh", "Anuradha Paudwal",
    "Sonu Nigam", "Abhijeet", "Sadhana Sargam", "Kavita Krishnamurthy", "Lata Mangeshkar",
    "Asha Bhosle", "S P B", "SPB", "Vinod Rathod", "Roop Kumar Rathod", "Babul Supriyo",
    "Alka Chandrakar", "Shreya Ghoshal", "Mohd. Aziz", "Mohd Aziz", "Agam Kumar Nigam",
    "Aditya Pancholi", "Vipin Sachdeva", "Poornima", "Chitra S", "Chitra", "Babla Mehta",
    "Javed Akhtar", "S. P. Balasubrahmanyam", "S P Balasubrahmanyam", "Laxmikant Pyarelal",
    "Nadeem Shravan", "Anu Malik", "Anand Milind", "Anand Raj Anand", "Rajesh Roshan",
    "कुमार शानू", "अलका याग्निक", "उदित नारायण", "साधना सरगम", "अनुराधा पौड़वाल",
    "सोनू निगम", "आशा भोसले", "लता मंगेशकर", "मोहम्मद अज़ीज़", "अलका चंद्राकर"
]

KNOWN_ACTORS_MOVIES = [
    "Akshay Kumar", "Aamir Khan", "Salman Khan", "Shah Rukh Khan", "Shahrukh Khan",
    "Govinda", "Ajay Devgn", "Ajay Devgan", "Raveena Tandon", "Divya Bharti",
    "Pooja Bhatt", "Madhuri Dixit", "Sunil Shetty", "Rani Mukherjee", "Rani Mukerji",
    "Karisma Kapoor", "Karisma", "Twinkle Khanna", "Saif Ali Khan", "Bipasha Basu",
    "Dino Morea", "Rishi Kapoor", "Sanjay Kapoor", "Akshaye Khanna", "Juhi Chawla",
    "Mithun Chakraborty", "Mithun", "Preity Zinta", "Mahima Chaudhry", "Bobby Deol",
    "Hrithik Roshan", "Priyanka Chopra", "Tusshar Kapoor", "Kareena Kapoor", "Shilpa Shetty",
    "Sanjay Dutt", "Sunny Deol", "Tabu", "Mamta Kulkarni", "Jeetendra", "Reena Roy"
]

SUPPORTED_EXTENSIONS = {
    '.mp3', '.wav', '.m4a', '.aac', '.ogg', '.mp4', '.mpeg', '.flv', '.wma', '.flac'
}


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\s_]+', ' ', text).strip()
    return text


def parse_filename(filename):
    """
    Intelligently parses filename into (Title, Artist).
    Cleans video quality tags, suffixes, and separates song title from artist.
    """
    name_without_ext, _ = os.path.splitext(filename)

    # 1. Clean quality/downloader suffix tags like (0), (256k), (360p), (1080p), (0)(1), #bollywood
    stem = re.sub(r'\(\d+k\)', '', name_without_ext, flags=re.IGNORECASE)
    stem = re.sub(r'\(\d+p\)', '', stem, flags=re.IGNORECASE)
    stem = re.sub(r'\(\d+\)', '', stem)
    stem = re.sub(r'#\w+', '', stem)

    stem = stem.strip()
    if not stem:
        stem = name_without_ext

    # 2. Check for major separator triple/double underscore '___' or '__'
    if '___' in stem or '__' in stem:
        parts = re.split(r'___|__', stem)
        parts = [clean_text(p) for p in parts if clean_text(p)]

        if parts:
            raw_title = parts[0]
            raw_title = re.sub(
                r'\b(Lyrical Video|Full Video Song|Full Video|HD Video|4K Video|4K|Video Song|Full Song|Lyrical|Song|90s Romantic Song|90_s_Evergreen_Romantic_Song|Evergreen Romantic Song|Best Of|Love Song)\b.*$',
                '', raw_title, flags=re.IGNORECASE
            ).strip()
            raw_title = re.sub(r'[-–—|]+$', '', raw_title).strip()
            title = raw_title if raw_title else parts[0]

            found_singers = []
            for part in parts[1:]:
                for singer in KNOWN_SINGERS:
                    if re.search(r'\b' + re.escape(singer) + r'\b', part, flags=re.IGNORECASE):
                        if singer not in found_singers:
                            found_singers.append(singer)

            if found_singers:
                artist = ", ".join(found_singers)
            else:
                candidate = parts[-1]
                is_actor = any(re.search(r'\b' + re.escape(act) + r'\b', candidate, flags=re.IGNORECASE) for act in KNOWN_ACTORS_MOVIES)
                if not is_actor and len(candidate) < 50:
                    artist = candidate
                else:
                    artist = ""
            return clean_text(title)[:150], clean_text(artist)[:150]

    # 3. Check for standard separators: ' - ', ' – ', ' — ', ' | ', '_-_', '-', '–', '|'
    sep_match = re.search(r'\s*[\-–—|]\s*', stem)
    if sep_match:
        parts = re.split(r'\s*[\-–—|]\s*', stem, maxsplit=1)
        if len(parts) == 2:
            p0 = clean_text(parts[0])
            p1 = clean_text(parts[1])

            p0_clean = re.sub(
                r'\b(Lyrical Video|Full Video Song|Full Video|HD Video|4K Video|4K|Video Song|Full Song|Lyrical)\b.*$',
                '', p0, flags=re.IGNORECASE
            ).strip()
            title = p0_clean if p0_clean else p0

            p0_has_singer = any(re.search(r'\b' + re.escape(s) + r'\b', p0, re.IGNORECASE) for s in KNOWN_SINGERS)
            p1_has_singer = any(re.search(r'\b' + re.escape(s) + r'\b', p1, re.IGNORECASE) for s in KNOWN_SINGERS)

            if p1_has_singer and not p0_has_singer:
                artist = p1
            elif p0_has_singer and not p1_has_singer:
                artist = p0
                title = p1
            else:
                artist = p1

            return clean_text(title)[:150], clean_text(artist)[:150]

    # 4. Fallback if no separator split with high confidence:
    title = clean_text(stem)
    title = re.sub(
        r'\b(Lyrical Video|Full Video Song|Full Video|HD Video|4K Video|4K|Video Song|Full Song|Lyrical)\b.*$',
        '', title, flags=re.IGNORECASE
    ).strip()
    return clean_text(title)[:150], ""


def sanitize_filename(filename):
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'[^\w\.\-\(\)]', '_', name)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    if not clean_name:
        clean_name = "song"
    return clean_name + ext.lower()


def auto_import_songs():
    """
    Scans songs folder and automatically imports all songs into SQLite database and media directory.
    Safe to run repeatedly.
    """
    try:
        songs_dir = settings.BASE_DIR / 'booking' / 'static' / 'images' / 'pikipwaladetails' / 'song'
        if not os.path.exists(songs_dir):
            return

        all_files = os.listdir(songs_dir)
        audio_files = [
            f for f in sorted(all_files)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        ]

        if not audio_files:
            return

        media_dest_dir = settings.MEDIA_ROOT / 'pickupwala' / 'songs'
        os.makedirs(media_dest_dir, exist_ok=True)

        db_path = settings.BASE_DIR / 'db.sqlite3'
        if not os.path.exists(db_path):
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pickupwala_song (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(150) NOT NULL,
                artist VARCHAR(150) NOT NULL,
                audio_file VARCHAR(100) NOT NULL,
                cover_image VARCHAR(100) NULL,
                duration_seconds UNSIGNED INT NOT NULL DEFAULT 0,
                trip_km UNSIGNED INT NOT NULL DEFAULT 150,
                is_active BOOL NOT NULL DEFAULT 1,
                "order" UNSIGNED INT NOT NULL DEFAULT 0,
                added_on DATETIME NOT NULL
            )
        ''')

        # Get existing songs audio files & titles
        cursor.execute("SELECT audio_file, LOWER(title), LOWER(artist) FROM pickupwala_song")
        existing_rows = cursor.fetchall()
        existing_files = {row[0].lower() for row in existing_rows}
        existing_titles = {(row[1], row[2]) for row in existing_rows}

        cursor.execute("SELECT MAX(\"order\") FROM pickupwala_song")
        max_order_row = cursor.fetchone()
        current_order = (max_order_row[0] or 0) + 1 if max_order_row else 1

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_count = 0

        for filename in audio_files:
            title, artist = parse_filename(filename)
            clean_file = sanitize_filename(filename)
            rel_audio_path = f"pickupwala/songs/{clean_file}"

            src_path = songs_dir / filename
            dest_path = media_dest_dir / clean_file

            # Copy file to media directory if missing
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(src_path, dest_path)
                except Exception:
                    pass

            # Update existing DB record to use sanitized filename if needed
            cursor.execute("UPDATE pickupwala_song SET audio_file=? WHERE LOWER(title)=? AND (audio_file LIKE '%#%' OR audio_file LIKE '% %' OR audio_file LIKE '%🌧%')",
                           (rel_audio_path, title.lower()))

            if rel_audio_path.lower() in existing_files or (title.lower(), artist.lower()) in existing_titles:
                continue

            cursor.execute('''
                INSERT INTO pickupwala_song (title, artist, audio_file, cover_image, duration_seconds, trip_km, is_active, "order", added_on)
                VALUES (?, ?, ?, NULL, 0, 150, 1, ?, ?)
            ''', (title if title else clean_file, artist, rel_audio_path, current_order, now_str))

            current_order += 1
            new_count += 1

        conn.commit()
        conn.close()

        if new_count > 0:
            print(f"✅ Auto-imported {new_count} Pickupwala Radio songs into db.sqlite3!")
            print(f"✅ Auto-imported {new_count} Pickupwala Radio songs into db.sqlite3!")

    except Exception as e:
        print("Auto import notice:", e)
