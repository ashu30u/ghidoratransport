import os
import sqlite3
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from .models import Shayari, Song, ChaiMessage, HornSound

DEFAULT_CHAI_MESSAGES = [
    {"title": "Chai ka time ho gaya! ☕", "message": "Safar ke beech ek garma-garam chai toh banti hai! 🚚☕"},
    {"title": "Chai Break! ☕😎", "message": "Thoda rukna banta hai, chai peena zaroori hai!"},
    {"title": "Ek Cup Chai Ho Jaye! ☕", "message": "Thakan ko thoda side karo, chai ka maza lo! 😍"},
    {"title": "Chai Pe Charcha! ☕", "message": "Safar bhi chalega aur chai bhi! 🚚😄"},
    {"title": "Chai Ready Hai! ☕🔥", "message": "Kadak chai ke bina safar adhoora hai!"},
    {"title": "Ruk Jaao Zara! ☕", "message": "Chai ki khushboo bula rahi hai! 😋"},
    {"title": "Chai Time Alert! 🚨☕", "message": "Engine thoda rest, driver sahab chai best! 😎"},
    {"title": "Kadak Chai, Fresh Mood! ☕✨", "message": "Ek cup chai aur phir safar full speed!"},
    {"title": "Safar Lamba Hai Janaab! 🚚", "message": "Beech mein chai ka break toh banta hai! ☕"},
    {"title": "Chai Se Refresh Ho Jao! ☕💪", "message": "Thodi chai, thoda aaram, phir safar tamaam!"},
    {"title": "Chai Bina Kya Safar! ☕😂", "message": "Ek cup chai lo aur mood bana lo!"},
    {"title": "Chai Lovers, Break Lo! ❤️☕", "message": "Aaj ki chai miss mat karna!"},
    {"title": "Garam Chai, Thanda Dimaag! ☕😄", "message": "Pehle chai, phir agli manzil!"},
    {"title": "Chai Ka Mood Ban Raha Hai! ☕😍", "message": "Ab break lena toh zaroori hai!"},
    {"title": "Chai Break = Energy Break! ⚡☕", "message": "Ek cup chai aur phir full energy!"},
    {"title": "Chai Ki Khushboo Aa Rahi Hai! ☕👃", "message": "Lagta hai break ka waqt ho gaya!"},
    {"title": "Driver Bhai, Chai Ho Jaye! 🚚☕", "message": "Safar ke saath chai bhi zaroori hai!"},
    {"title": "Ek Kadak Chai Please! ☕🔥", "message": "Thakan ka desi ilaaj — chai!"},
    {"title": "Chai Pehle, Safar Baad Mein! 😎☕", "message": "Aaj chai ka break banta hai!"},
    {"title": "Mood Off? Chai On! ☕😄", "message": "Ek cup chai aur mood ekdum fresh!"},
    {"title": "Chai Hai Toh Safar Hai! 🚚☕", "message": "Chai ke bina journey incomplete!"},
    {"title": "Thoda Aaram, Thodi Chai! ☕❤️", "message": "Safar ko banaye aur bhi suhana!"},
    {"title": "Chai Break Ka Signal! 🚦☕", "message": "Thodi der ruk jao, chai pee lo!"},
    {"title": "Chai Ka Ek Cup, Energy Full! ⚡☕", "message": "Ab agli manzil ke liye ready!"},
    {"title": "Chai Wali Feeling! 😍☕", "message": "Garma-garam chai aur mast safar!"},
    {"title": "Aaj Ki Chai Ho Jaye! ☕", "message": "Break chhota sa, sukoon bada sa!"},
    {"title": "Chai Time, Smile Time! 😊☕", "message": "Ek cup chai aur ek pyari si smile!"},
    {"title": "Safar Mein Chai Zaroori Hai! 🚚☕", "message": "Driver bhai, apna chai break miss na karein!"},
    {"title": "Chai Ki Talaash Khatam! ☕😋", "message": "Ab bas ek cup aur thoda aaram!"},
    {"title": "Chai Break Lagao! ☕🔥", "message": "Thakan bhagao aur energy badhao!"},
    {"title": "Chai Aur Sukoon! ❤️☕", "message": "Safar ke beech thoda sukoon bhi zaroori hai!"},
    {"title": "Chai Ka Break, Dil Ka Sukoon! ☕😌", "message": "Ek cup chai aur sab set!"},
    {"title": "Chai Peelo Bhai! 😄☕", "message": "Safar lamba hai, energy banaye rakho!"},
    {"title": "Kadak Chai Ki Pukaar! ☕🔥", "message": "Kya aap sun rahe ho? Break ka time hai!"},
    {"title": "Chai Time, No Tension! 😎☕", "message": "Thoda relax karo, phir safar continue karo!"},
    {"title": "Chai Ki Chuski, Safar Ki Masti! 🚚☕", "message": "Break lo aur fresh ho jao!"},
    {"title": "Ek Break Toh Banta Hai! ☕😉", "message": "Aur break mein chai toh pakki hai!"},
    {"title": "Chai Ready, Driver Ready! 🚚☕", "message": "Pehle chai, phir drive!"},
    {"title": "Chai Se Din Ban Jata Hai! ☕❤️", "message": "Aaj ka chai break miss mat karo!"},
    {"title": "Chai Break: Activated! ☕✅", "message": "Thoda rest, thodi chai, phir full power!"}
]

DEFAULT_SHAYARI_LIST = [
    "सफ़र खूबसूरत हो जाता है, जब साथ मुस्कुराने वाला हो। ❤️",
    "मंज़िल की फिक्र नहीं, सफ़र का मज़ा लेते चलो। 🚚✨",
    "रास्ते चाहे कितने भी लंबे हों, हौसला छोटा नहीं होना चाहिए। 💪",
    "ज़िंदगी एक सफ़र है जनाब, हर मोड़ पर एक कहानी है। ❤️",
    "रास्ते बदलते रहे, हम सफ़र करते रहे। 🚚",
    "मुस्कुराते रहिए, क्योंकि सफ़र अभी बाकी है। 😊",
    "मंज़िल उन्हीं को मिलती है, जो रास्तों से घबराते नहीं। ✨",
    "सफ़र में सुकून चाहिए तो दिल में मुस्कान रखिए। ❤️",
    "रास्ता लंबा हो तो क्या हुआ, हौसला तो साथ है। 💪",
    "हर सफ़र कुछ सिखाता है, बस सीखने वाला दिल चाहिए। 🌄",
    "चल पड़े हैं मंज़िल की ओर, अब रास्ते खुद कहानी कहेंगे। 🚚✨",
    "ज़िंदगी की राहों में मुस्कुराना भी एक हुनर है। 😊",
    "सफ़र छोटा हो या लंबा, यादें हमेशा खूबसूरत होनी चाहिए। ❤️",
    "जहाँ रास्ते खत्म होते हैं, वहीं से नई मंज़िल शुरू होती है। ✨",
    "वक्त बदलता है, रास्ते बदलते हैं, मगर हौसले नहीं बदलने चाहिए। 💪",
    "सफ़र में थक जाओ तो रुक जाना, हार मत मानना। ❤️",
    "मंज़िल का मज़ा तभी है, जब रास्ता दिल से तय किया हो। 🚚",
    "हर मोड़ पर उम्मीद रखो, हर रास्ते पर भरोसा रखो। 🌟",
    "रास्ते कठिन हैं तो क्या, इरादे मजबूत हैं। 💪",
    "चलते रहो मुस्कुराते हुए, मंज़िल खुद करीब आएगी। 😊",
    "कुछ रास्ते मंज़िल से भी ज्यादा खूबसूरत होते हैं। 🌄",
    "सफ़र वही यादगार होता है, जिसमें दिल खुश रहता है। ❤️",
    "हौसला रखिए जनाब, रास्ते खुद आसान होते जाएंगे। ✨",
    "आज का सफ़र, कल की खूबसूरत याद बन जाएगा। 🚚❤️",
    "जो सफ़र दिल से किया जाए, वो कभी बेकार नहीं जाता। 💫",
    "रास्तों की परवाह मत करो, अपने हौसलों की परवाह करो। 💪",
    "मुस्कान साथ रखो, सफ़र अपने आप सुहाना हो जाएगा। 😊",
    "मंज़िल मिले या ना मिले, सफ़र का मज़ा कम नहीं होना चाहिए। ❤️",
    "हर सुबह एक नई राह, हर राह एक नई उम्मीद। 🌅",
    "सफ़र में साथी अच्छे हों, तो रास्ते भी छोटे लगते हैं। ❤️",
    "ज़िंदगी की गाड़ी चलती रहे, बस मुस्कान बनी रहे। 🚚😊",
    "राहों में मुश्किलें आएँगी, मगर रुकना हमारी फितरत नहीं। 💪",
    "सफ़र लंबा है तो क्या, दिल में जुनून बाकी है। 🔥",
    "रास्ते हजार मिलेंगे, बस मंज़िल पर नज़र रखो। ✨",
    "चलना है तो मुस्कुराकर चलो, जिंदगी दोबारा नहीं मिलती। ❤️",
    "हर सफ़र में एक नया अनुभव, हर अनुभव में एक नई कहानी। 📖",
    "थकान रास्ते की है, हौसला दिल का है। 💪",
    "मंज़िल की चाहत हो तो रास्तों से दोस्ती करनी पड़ती है। ❤️",
    "सफ़र में सुकून हो तो दूरी मायने नहीं रखती। 🌄",
    "चलते रहो, क्योंकि रुकने वालों की मंज़िल कभी नहीं आती। 🚚✨",
    "जिंदगी के रास्ते आसान नहीं, मगर खूबसूरत जरूर हैं। ❤️",
    "सफ़र का असली मज़ा मंज़िल में नहीं, रास्तों में है। 🌄",
    "हौसला बुलंद हो तो हर रास्ता आसान लगता है। 💪",
    "आज फिर निकल पड़े हैं, एक नई मंज़िल की तलाश में। 🚚",
    "रास्ते चाहे अनजान हों, भरोसा अपने कदमों पर रखो। ✨",
    "मुस्कान छोटी सी चीज़ है, मगर सफ़र खूबसूरत बना देती है। 😊",
    "सफ़र करते रहिए, यादें अपने आप बनती रहेंगी। ❤️",
    "जिंदगी की राहों में बस हिम्मत और मुस्कान चाहिए। 🌟",
    "हर मंज़िल से पहले कई रास्ते पार करने पड़ते हैं। 🚚",
    "सफ़र जारी है जनाब, कहानी अभी बाकी है। ❤️🔥"
]


def seed_data_sqlite():
    """Populates all 40 Chai Messages AND 50 Shayari lines directly into db.sqlite3 for Django Admin."""
    try:
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Seed Chai Messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pickupwala_chaimessage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(150) NOT NULL,
                message VARCHAR(300) NOT NULL,
                is_active BOOL NOT NULL DEFAULT 1,
                "order" UNSIGNED INT NOT NULL DEFAULT 0
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM pickupwala_chaimessage")
        chai_count = cursor.fetchone()[0]
        if chai_count < 10:
            cursor.execute("DELETE FROM pickupwala_chaimessage")
            for idx, item in enumerate(DEFAULT_CHAI_MESSAGES):
                cursor.execute(
                    'INSERT INTO pickupwala_chaimessage (title, message, is_active, "order") VALUES (?, ?, 1, ?)',
                    (item["title"], item["message"], idx)
                )
            conn.commit()

        # 2. Seed Shayari lines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pickupwala_shayari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text VARCHAR(300) NOT NULL,
                is_active BOOL NOT NULL DEFAULT 1,
                "order" UNSIGNED INT NOT NULL DEFAULT 0
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM pickupwala_shayari")
        shayari_count = cursor.fetchone()[0]
        if shayari_count < 10:
            cursor.execute("DELETE FROM pickupwala_shayari")
            for idx, text in enumerate(DEFAULT_SHAYARI_LIST):
                cursor.execute(
                    'INSERT INTO pickupwala_shayari (text, is_active, "order") VALUES (?, 1, ?)',
                    (text, idx)
                )
            conn.commit()

        conn.close()
    except Exception as e:
        print("SQLite data seeding notice:", e)


# Run direct database seeding on import
seed_data_sqlite()


def player_page(request):
    """Renders the Pickupwala player."""
    return render(request, "pickupwala/player.html")


def playlist_api(request):
    """Returns songs + shayari lines + chai messages for the player."""
    seed_data_sqlite()
    songs = Song.objects.filter(is_active=True).order_by("order", "id")
    tracks = []
    for s in songs:
        audio_url = s.audio_file.url if s.audio_file else ""
        if not audio_url:
            audio_url = "https://stream.zeno.fm/f3wvbb142p8uv"
            
        tracks.append({
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "audio_url": audio_url,
            "cover_url": s.cover_image.url if s.cover_image else "",
            "duration": s.duration_seconds or 200,
            "km": s.trip_km,
        })

    try:
        shayari = list(
            Shayari.objects.filter(is_active=True).order_by("order", "id").values_list("text", flat=True)
        )
    except Exception:
        shayari = DEFAULT_SHAYARI_LIST

    if not shayari:
        shayari = DEFAULT_SHAYARI_LIST

    try:
        chai = list(
            ChaiMessage.objects.filter(is_active=True).order_by("order", "id").values("title", "message")
        )
    except Exception:
        chai = DEFAULT_CHAI_MESSAGES

    if not chai:
        chai = DEFAULT_CHAI_MESSAGES

    horns = []
    try:
        for h in HornSound.objects.filter(is_active=True).order_by("order", "id"):
            if h.audio_file:
                horns.append({"id": h.id, "title": h.title, "url": h.audio_file.url})
    except Exception:
        horns = []

    return JsonResponse({"tracks": tracks, "shayari": shayari, "chai": chai, "horns": horns})
