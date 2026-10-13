import os
import re
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models
from pickupwala.models import Song

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
            # Remove common fluff words at the end of title
            raw_title = re.sub(
                r'\b(Lyrical Video|Full Video Song|Full Video|HD Video|4K Video|4K|Video Song|Full Song|Lyrical|Song|90s Romantic Song|90_s_Evergreen_Romantic_Song|Evergreen Romantic Song|Best Of|Love Song)\b.*$',
                '', raw_title, flags=re.IGNORECASE
            ).strip()
            raw_title = re.sub(r'[-–—|]+$', '', raw_title).strip()
            title = raw_title if raw_title else parts[0]

            # Find singers in remaining parts
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


class Command(BaseCommand):
    help = "Automatically imports music/audio files from the static songs folder into Pickupwala Radio Songs database."

    def handle(self, *args, **options):
        songs_dir = settings.BASE_DIR / 'booking' / 'static' / 'images' / 'pikipwaladetails' / 'song'

        if not os.path.exists(songs_dir):
            self.stdout.write(self.style.ERROR(f"Songs folder not found at: {songs_dir}"))
            return

        all_files = os.listdir(songs_dir)
        audio_files = [
            f for f in sorted(all_files)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        ]

        total_found = len(audio_files)
        self.stdout.write(self.style.MIGRATE_HEADING(f"Found {total_found} audio files\n"))

        media_dest_dir = settings.MEDIA_ROOT / 'pickupwala' / 'songs'
        os.makedirs(media_dest_dir, exist_ok=True)

        max_order = Song.objects.aggregate(max_order=models.Max('order'))['max_order'] or 0
        current_order = max_order + 1

        imported_list = []
        skipped_count = 0
        failed_count = 0

        for idx, filename in enumerate(audio_files, 1):
            try:
                title, artist = parse_filename(filename)

                # Duplicate check by audio_file or title/artist match
                rel_audio_path = f"pickupwala/songs/{filename}"
                exists = (
                    Song.objects.filter(audio_file__icontains=filename).exists() or
                    Song.objects.filter(title__iexact=title, artist__iexact=artist).exists()
                )

                if exists:
                    skipped_count += 1
                    continue

                # Copy file to media directory if not already there
                src_path = songs_dir / filename
                dest_path = media_dest_dir / filename
                if not os.path.exists(dest_path):
                    shutil.copy2(src_path, dest_path)

                # Create Song record
                song = Song.objects.create(
                    title=title if title else filename,
                    artist=artist,
                    audio_file=rel_audio_path,
                    cover_image=None,  # Intentionally blank cover image
                    duration_seconds=0,  # Fallback to audio player duration
                    trip_km=150,  # Default trip distance
                    is_active=True,
                    order=current_order
                )
                current_order += 1

                display_artist = f" — {artist}" if artist else ""
                imported_list.append(f"{title}{display_artist}")

            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f"Failed to import '{filename}': {e}"))

        self.stdout.write(self.style.SUCCESS("Imported:"))
        if imported_list:
            for i, name in enumerate(imported_list, 1):
                self.stdout.write(f"  {i}. {name}")
        else:
            self.stdout.write("  (No new songs to import)")

        self.stdout.write("")
        self.stdout.write(self.style.WARNING(f"Skipped existing: {skipped_count}"))
        self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import completed successfully."))
