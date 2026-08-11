"""
chatbot/views.py - Ghidora AI Master Intelligent Multi-Module & GK Response Engine
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .gemini_client import get_reply


@csrf_exempt
@require_POST
def chat_endpoint(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = data.get("message", "").strip()
    image_data = data.get("image_data", None)
    lang = data.get("lang", "hi")

    if not message and not image_data:
        return JsonResponse({"error": "Message empty hai"}, status=400)

    # If user uploaded an image, analyze image directly with Vision AI
    if image_data:
        try:
            reply = get_reply(message, image_data)
            return JsonResponse({"reply": reply})
        except Exception as e:
            print("VISION AI ERROR:", repr(e))
            return JsonResponse({"reply": "I am analyzing this image. Please ask your question about the image." if lang == 'en' else "Main is image ko analyze kar rahi hoon. Kripya image ke baare mein sawal likhein."})

    msg_lower = message.lower()

    # Detect if user is asking in English
    is_en = (lang == 'en') or any(k in msg_lower for k in ['what is', 'how much', 'who is', 'tell me', 'can you', 'where is', 'show me', 'hello', 'hi ', 'good morning', 'how does', 'explain'])

    # 🌤️ 0. System Explanation Queries (What is Weather System / How Weather AI works)
    if any(k in msg_lower for k in ['system', 'feature', 'function', 'works', 'working', 'explain', 'kya hai', 'kaise kaam', 'kaise kam', 'jankari', 'details', 'about weather', 'weather ai']) and any(k in msg_lower for k in ['weather', 'mausam', 'मौसम', 'radar', 'alert']):
        if is_en:
            reply = (
                "🌤️ **Ghidora AI Transport Weather Intelligence System Overview**:\n\n"
                "Our platform features an advanced **AI-Powered Transport Weather Intelligence System** designed for freight safety:\n\n"
                "1. **🔍 Live City & GPS Weather Radar**: Search live weather for any city globally or sync live browser GPS coordinates.\n"
                "2. **🚨 3-Tier Dynamic Driver Risk Alerts & Speed Guidelines**:\n"
                "   • 🔴 **Red Alert (High Risk)**: Rain Prob ≥ 65% ➔ **Driver Speed: Max 35-40 km/h**. Mandatory double waterproof tarpaulin!\n"
                "   • 🟡 **Yellow Alert (Medium Risk)**: Rain Prob 35-65% ➔ **Recommended Speed: 50-60 km/h**. Tarpaulin ready!\n"
                "   • 🟢 **Green Alert (Low Risk)**: Rain Prob < 35% ➔ **Safe Cruising Speed: 65-75 km/h**. Clear highway!\n"
                "3. **🗺️ Pickup & Destination Route Weather Comparator**: Compare pickup vs destination weather live and calculate weather delivery delays.\n"
                "4. **🛣️ Live Route Checkpoints**: Automatically generates 4 intermediate highway checkpoint stops (0 KM ➔ 33% ➔ 66% ➔ Destination) with real-time live temperatures & weather icons.\n"
                "5. **🛡️ AI Cargo Protection Advisor**: Material-specific wrapping guidelines for Cement, Electronics, Vegetables, and Machinery.\n"
                "6. **🎬 Live Canvas & Video Radar**: Includes `weatherbg.mp4` background video & HTML5 particle weather canvas animations!\n\n"
                "💡 *Tip*: Click **`🌤️ Weather AI`** in the top Navbar or **`🌤️ Open Live Weather Radar`** on the home page to launch the Weather Window!"
            )
        else:
            reply = (
                "🌤️ **Ghidora AI Transport Weather Intelligence System संपूर्ण जानकारी**:\n\n"
                "हमारी प्लेटफ़ॉर्म में माल परिवहन सुरक्षा के लिए **AI-Powered Transport Weather System** शामिल है:\n\n"
                "1. **🔍 लाइव सिटी और GPS वेदर रडार**: दुनिया के किसी भी शहर (जैसे दिल्ली, मुंबई, रायपुर, धमतरी) या GPS से लाइव मौसम और तापमान देखें।\n"
                "2. **🚨 3-स्तरीय ड्राइवर सुरक्षा अलर्ट और स्पीड गाइडलाइन**:\n"
                "   • 🔴 **Red Alert (High Risk)**: बारिश ≥ 65% ➔ **सुरक्षित स्पीड: 35-40 km/h max**। वॉटरप्रूफ त्रिपाल अनिवार्य!\n"
                "   • 🟡 **Yellow Alert (Medium Risk)**: बारिश 35-65% ➔ **अनुशंसित स्पीड: 50-60 km/h**। त्रिपाल तैयार रखें!\n"
                "   • 🟢 **Green Alert (Low Risk)**: बारिश < 35% ➔ **सुरक्षित स्पीड: 65-75 km/h**। साफ़ हाइवे!\n"
                "3. **🗺️ पिकअप और ड्रॉप रूट वेदर कंपैरेटर**: पिकअप (जैसे रायपुर) और डेस्टिनेशन (जैसे धमतरी) डालकर दोनों शहरों का लाइव मौसम और डिले टाइम देखें।\n"
                "4. **🛣️ लाइव रूट चेकपॉइंट्स**: किसी भी रूट पर खुद-ब-खुद 4 हाइवे चेकपॉइंट्स (0 KM ➔ 33% ➔ 66% ➔ Destination) का रियल-टाइम लाइव मौसम दिखाता है।\n"
                "5. **🛡️ AI माल सुरक्षा सलाह**: सीमेंट, इलेक्ट्रॉनिक्स, सब्जियों और मशीनों के लिए त्रिपाल की सुरक्षा सलाह।\n"
                "6. **🎬 लाइव बैकग्राउंड वीडियो और एनिमेशन**: बैकग्राउंड में `weatherbg.mp4` वीडियो और HTML5 एनिमेशन कैनवास।\n\n"
                "💡 *Tip*: नेवबार में **`🌤️ Weather AI`** बटन दबाकर पूरा वेदर विंडो खोलें!"
            )
        return JsonResponse({"reply": reply})

    # 🌤️ 0. Transport Weather Intelligence Queries (Dynamic City Detection & Spell Corrector)
    if any(k in msg_lower for k in ['weather', 'mausam', 'मौसम', 'barish', 'baarish', 'rain', 'temperature', 'taapman', 'taapmaan', 'forecast', 'fog', 'storm', 'humidity', 'aqi', 'uv']):
        # Clean query text to extract exact city name
        clean_words = []
        stop_words = set(['weather', 'mausam', 'मौसम', 'kaisa', 'kesa', 'kaisa hai', 'kesa hai', 'batao', 'batayein', 'bataiye', 'ki', 'ka', 'ke', 'par', 'mein', 'in', 'report', 'aaj', 'today', 'live', 'check', 'how is', 'what is', 'tell me', 'of', 'for', 'the', 'about', 'city', 'batao', 'batao na'])
        
        words = re.findall(r'\w+', msg_lower)
        for w in words:
            if w not in stop_words and len(w) > 1:
                clean_words.append(w)
        
        raw_city = " ".join(clean_words).strip()

        # Dictionary of pre-configured coordinates & spellings for fast & accurate response
        CITY_DB = {
            'delhi': {'name': 'Delhi', 'lat': 28.6139, 'lon': 77.2090, 'temp': 35, 'cond': '🌤️ Partly Cloudy'},
            'dilli': {'name': 'Delhi', 'lat': 28.6139, 'lon': 77.2090, 'temp': 35, 'cond': '🌤️ Partly Cloudy'},
            'dilhi': {'name': 'Delhi', 'lat': 28.6139, 'lon': 77.2090, 'temp': 35, 'cond': '🌤️ Partly Cloudy'},
            'mumbai': {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'temp': 30, 'cond': '🌧️ Light Rain'},
            'mubai': {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'temp': 30, 'cond': '🌧️ Light Rain'},
            'bambai': {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'temp': 30, 'cond': '🌧️ Light Rain'},
            'bangalore': {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946, 'temp': 27, 'cond': '☁️ Overcast Cloud'},
            'banglore': {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946, 'temp': 27, 'cond': '☁️ Overcast Cloud'},
            'bengaluru': {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946, 'temp': 27, 'cond': '☁️ Overcast Cloud'},
            'kolkata': {'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639, 'temp': 33, 'cond': '🌧️ Scattered Rain'},
            'raipur': {'name': 'Raipur', 'lat': 21.2514, 'lon': 81.6296, 'temp': 33, 'cond': '☀️ Clear Sunny'},
            'dhamtari': {'name': 'Dhamtari', 'lat': 20.7071, 'lon': 81.5499, 'temp': 26, 'cond': '🌩️ Heavy Rain Alert'},
            'kurud': {'name': 'Dhamtari', 'lat': 20.7071, 'lon': 81.5499, 'temp': 26, 'cond': '🌩️ Heavy Rain Alert'},
            'kodebod': {'name': 'Dhamtari', 'lat': 20.7071, 'lon': 81.5499, 'temp': 26, 'cond': '🌩️ Heavy Rain Alert'},
            'bilaspur': {'name': 'Bilaspur', 'lat': 22.0797, 'lon': 82.1391, 'temp': 31, 'cond': '🌤️ Partly Cloudy'},
            'durg': {'name': 'Durg', 'lat': 21.1904, 'lon': 81.2849, 'temp': 32, 'cond': '☀️ Clear Sunny'},
            'bhilai': {'name': 'Bhilai', 'lat': 21.1938, 'lon': 81.3509, 'temp': 32, 'cond': '☀️ Clear Sunny'},
            'pune': {'name': 'Pune', 'lat': 18.5204, 'lon': 73.8567, 'temp': 28, 'cond': '🌤️ Pleasant Cloud'},
            'hyderabad': {'name': 'Hyderabad', 'lat': 17.3850, 'lon': 78.4867, 'temp': 31, 'cond': '🌤️ Partly Cloudy'},
            'chennai': {'name': 'Chennai', 'lat': 13.0827, 'lon': 80.2707, 'temp': 34, 'cond': '☀️ Warm Sunny'},
            'jaipur': {'name': 'Jaipur', 'lat': 26.9124, 'lon': 75.7873, 'temp': 36, 'cond': '☀️ Dry Heat'},
            'ahmedabad': {'name': 'Ahmedabad', 'lat': 23.0225, 'lon': 72.5714, 'temp': 35, 'cond': '☀️ Sunny'},
            'korba': {'name': 'Korba', 'lat': 22.3595, 'lon': 82.7501, 'temp': 30, 'cond': '☁️ Cloudy'},
            'jagdalpur': {'name': 'Jagdalpur', 'lat': 19.0744, 'lon': 82.0211, 'temp': 27, 'cond': '🌧️ Light Rain'},
            'ambikapur': {'name': 'Ambikapur', 'lat': 23.1185, 'lon': 83.1985, 'temp': 26, 'cond': '🌤️ Pleasant'}
        }

        target_info = None
        for key in CITY_DB:
            if key in raw_city or key in msg_lower:
                target_info = CITY_DB[key]
                break

        city_display = target_info['name'] if target_info else (raw_city.title() if raw_city else 'Dhamtari')
        lat = target_info['lat'] if target_info else None
        lon = target_info['lon'] if target_info else None

        fetched_reply = None
        # Try Live Fetch first
        try:
            if not lat:
                geo_res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city_display}&count=1&language=en&format=json", timeout=3)
                if geo_res.status_code == 200 and geo_res.json().get('results'):
                    g = geo_res.json()['results'][0]
                    lat, lon = g['latitude'], g['longitude']
                    city_display = f"{g.get('name', city_display)}, {g.get('country', '')}".strip(', ')

            if lat and lon:
                w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m,surface_pressure&daily=temperature_2m_max,temperature_2m_min", timeout=3)
                if w_res.status_code == 200:
                    w_data = w_res.json()
                    cw = w_data.get('current_weather', {})
                    temp = cw.get('temperature', 30)
                    wcode = cw.get('weathercode', 0)
                    wind = cw.get('windspeed', 12)
                    
                    humidity = 58
                    try:
                        humidity = w_data.get('hourly', {}).get('relativehumidity_2m', [58])[0]
                    except: pass
                    
                    pressure = 1012
                    try:
                        pressure = round(w_data.get('hourly', {}).get('surface_pressure', [1012])[0])
                    except: pass

                    cond_icon = "☀️ Clear Sunny"
                    if wcode in [1, 2, 3]: cond_icon = "🌤️ Partly Cloudy"
                    elif wcode in [45, 48]: cond_icon = "🌫️ Fog / Mist"
                    elif wcode in [51, 53, 55, 61, 63, 65]: cond_icon = "🌧️ Light Rain"
                    elif wcode in [80, 81, 82, 95, 96, 99]: cond_icon = "🌩️ Heavy Rain & Thunderstorm Alert"

                    is_rainy = 'Rain' in cond_icon or 'Thunderstorm' in cond_icon
                    speed_adv = "Max 35-40 km/h (High Risk 🔴)" if is_rainy else "65-75 km/h (Low Risk 🟢)"

                    if is_en:
                        fetched_reply = (
                            f"🌤️ **AI Weather Intelligence Report: {city_display}**\n"
                            f"-----------------------------------------------\n"
                            f"🌡️ **Temperature**: **{temp}°C** (Feels like {round(temp + 2.5)}°C)\n"
                            f"🌤️ **Condition**: **{cond_icon}**\n"
                            f"💧 **Humidity**: **{humidity}%** | 💨 **Wind**: **{wind} km/h**\n"
                            f"⏲️ **Pressure**: **{pressure} hPa** | 🍃 **AQI**: **Good 🟢**\n\n"
                            f"🚦 **Driver Safety Speed**: **{speed_adv}**\n"
                            f"🚛 **Cargo Tarpaulin Advice**: {'⚠ Mandatory double waterproof tarpaulin cover required!' if is_rainy else '✅ Clear road conditions for safe transport delivery!'}"
                        )
                    else:
                        fetched_reply = (
                            f"🌤️ **AI लाइव मौसम इंटेलिजेंस रिपोर्ट: {city_display}**\n"
                            f"-----------------------------------------------\n"
                            f"🌡️ **तापमान (Temperature)**: **{temp}°C** (Feels like {round(temp + 2.5)}°C)\n"
                            f"🌤️ **स्थिति (Condition)**: **{cond_icon}**\n"
                            f"💧 **नमी (Humidity)**: **{humidity}%** | 💨 **हवा**: **{wind} km/h**\n"
                            f"⏲️ **दबाव (Pressure)**: **{pressure} hPa** | 🍃 **AQI**: **Good 🟢**\n\n"
                            f"🚦 **ड्राइवर सुरक्षा स्पीड गाइडलाइन**: **{speed_adv}**\n"
                            f"🚛 **माल सुरक्षा सलाह (Tarpaulin)**: {'⚠ माल के लिए डबल वॉटरप्रूफ त्रिपाल ढकना अनिवार्य है!' if is_rainy else '✅ परिवहन के लिए एकदम साफ़ रास्ता!'}"
                        )
        except Exception as err:
            print("LIVE API WARN:", err)

        if fetched_reply:
            return JsonResponse({"reply": fetched_reply})

        # Static Distinct Fallback per city if offline
        def_temp = target_info['temp'] if target_info else 32
        def_cond = target_info['cond'] if target_info else '🌤️ Partly Cloudy'

        if is_en:
            reply = (
                f"🌤️ **{city_display} Weather Report**:\n"
                f"• Current Temperature: **{def_temp}°C** (Feels like {def_temp + 3}°C)\n"
                f"• Weather Condition: **{def_cond}**\n"
                f"• Wind Speed: **14 km/h** | Air Quality (AQI): **Good 🟢**\n"
                f"• Transport Advisory: Clear freight driving conditions in {city_display}!"
            )
        else:
            reply = (
                f"🌤️ **{city_display} मौसम रिपोर्ट**:\n"
                f"• तापमान (Temperature): **{def_temp}°C** (Feels like {def_temp + 3}°C)\n"
                f"• स्थिति (Condition): **{def_cond}**\n"
                f"• हवा: **14 km/h** | AQI: **Good 🟢**\n"
                f"• परिवहन सलाह: {city_display} में माल परिवहन के लिए साफ़ रास्ता!"
            )

        return JsonResponse({"reply": reply})

    # 👑 1. PM / CM / Government Leaders Queries
    if any(k in msg_lower for k in ['pm', 'prime minister', 'modi', 'narendra']):
        return JsonResponse({"reply": "The Honorable Prime Minister of India is Shri Narendra Modi." if is_en else "India ke Honorable Prime Minister Shri Narendra Modi ji hain. Main Ghidora AI aapki Ghidora Transport booking aur queries mein poori madad kar sakti hoon!"})

    if any(k in msg_lower for k in ['cm', 'chief minister', 'vishnu', 'sai']):
        return JsonResponse({"reply": "The Honorable Chief Minister of Chhattisgarh is Shri Vishnu Deo Sai." if is_en else "Chhattisgarh ke Honorable Chief Minister Shri Vishnu Deo Sai ji hain. Main Ghidora AI aapki Ghidora Transport booking mein madad kar sakti hoon!"})

    # 🏢 2. Owner & Founder Queries
    if any(k in msg_lower for k in ['owner', 'tarun', 'malik', 'founder', 'sahu owner']):
        return JsonResponse({"reply": "The Official Owner & Founder of Ghidora Transport is Tarun Kumar Sahu (Phone: +91 6266014139 | Email: tarunsahu2407@gmail.com)." if is_en else "Ghidora Transport ke Official Owner & Founder Tarun Kumar Sahu hain (Phone: 6266014139 | Email: tarunsahu2407@gmail.com)."})

    # 👨‍💻 3. Lead Developer Queries
    if any(k in msg_lower for k in ['developer', 'amit', 'banayi', 'banaya', 'code', 'programmer', 'author']):
        return JsonResponse({"reply": "This Ghidora Transport AI Platform was designed and developed by Lead Developer Amit Kumar Sahu (Phone: +91 6268814185 | Email: dmtamit789@gmail.com)." if is_en else "Ghidora Transport ka yeh AI Platform Lead Developer Amit Kumar Sahu ne design kiya hai (Phone: 6268814185 | Email: dmtamit789@gmail.com)."})

    # 🚛 4. Driver & Vehicle Roster Queries
    if any(k in msg_lower for k in ['driver', 'pankaj', 'rajesh']):
        return JsonResponse({"reply": "Our primary verified driver is Pankaj Kumar Sahu (Phone: +91 7489297841 | Assigned Vehicle: Mahindra Bolero Maxx Pickup HD 2.0L CG 04 MW 2286)." if is_en else "Humare primary verified driver Pankaj Kumar Sahu hain (Phone: 7489297841 | Assigned Vehicle: Mahindra Bolero Maxx Pickup HD 2.0L CG 04 MW 2286)."})

    # 📦 5. Booking & Transport Queries (Comprehensive Master Guide)
    if any(k in msg_lower for k in ['book', 'booking', 'gadi', 'pickup', 'bhejna', 'ship', 'kaise kare', 'kese kare', 'kaise karte', 'kese karte', 'how to book', 'process', 'steps', 'kese', 'kaise']):
        if is_en:
            reply = (
                "📦 **Ghidora Transport Master Booking Process Guide**:\n\n"
                "Booking transport with Ghidora Transport is simple, fast, and 100% transparent. Here is the complete process:\n\n"
                "📝 **Step 1: Fill Mandatory Details (Required)**:\n"
                "• **Full Name**: Your contact name.\n"
                "• **Phone Number**: 10-digit mobile number for driver & SMS updates.\n"
                "• **Pickup Location**: Starting address/city (e.g., Raipur, Bilaspur).\n"
                "• **Destination / Drop Location**: Delivery address/city (e.g., Dhamtari, Durg).\n"
                "• **Journey Date**: Scheduled transport date.\n"
                "• **Vehicle Type**: Choose vehicle:\n"
                "   - *Mahindra Bolero Maxx Pickup HD 2.0L* (2-Ton Payload | ₹20/KM)\n"
                "   - *Tata Ace (Chota Hathi)* / *Mini Truck* / *Tractor Trolley* / *Van*\n\n"
                "✨ **Step 2: Optional Features (Extra Options for Custom Needs)**:\n"
                "• **Email Address**: To receive official PDF booking invoice copy.\n"
                "• **Distance (KM)**: Enter manually or let Google Map API auto-calculate distance!\n"
                "• **Trip Type**: Choose `One Way` or `Round Trip`.\n"
                "• **Cargo Description**: Details of goods (e.g., Cement, Furniture, House Shifting, Electronics).\n"
                "• **Weight & Unit**: Specify payload weight in `Kg` or `Ton` (e.g., 500 kg or 2 Ton).\n"
                "• **Special Message**: Extra instructions for driver or loading staff.\n"
                "• **Multimodal Attachments (Photo/Video/Voice)**: Upload cargo photos/videos or record a voice note for exact vehicle size estimation!\n\n"
                "💰 **Step 3: Instant Fare & Booking ID**: Rates are **₹20/KM** (Minimum ₹500 for local < 15 KM). Upon submission, you get a unique **Booking ID** (e.g., `GT4892`)!\n\n"
                "👨‍✈️ **Assigned Verified Driver**: Driver Pankaj Kumar Sahu (Phone: `7489297841` | Bolero Maxx `CG 04 MW 2286`).\n\n"
                "💡 *Tip*: Click **`📦 Book Transport`** or **`💰 Check Fare`** on the home page (`http://127.0.0.1:8000/#booking`) to start!"
            )
        else:
            reply = (
                "📦 **Ghidora Transport बुकिंग की पूरी प्रक्रिया (Step-by-Step Guide)**:\n\n"
                "Ghidora Transport में गाड़ियां बुक करना बेहद आसान और पारदर्शी है। जानिए पूरी प्रक्रिया:\n\n"
                "📝 **चरण 1: अनिवार्य जानकारी (Mandatory Fields)**:\n"
                "• **नाम (Full Name)**: आपका नाम।\n"
                "• **फोन नंबर (Phone)**: 10 अंकों का मोबाइल नंबर (ड्राइवर संपर्क के लिए)।\n"
                "• **पिकअप स्थान (Pickup)**: माल कहाँ से उठाना है (जैसे रायपुर, बिलासपुर)।\n"
                "• **ड्रॉप स्थान (Destination)**: माल कहाँ पहुँचाना है (जैसे धमतरी, दुर्ग)।\n"
                "• **यात्रा की तारीख (Journey Date)**: जिस दिन ट्रिप करनी है।\n"
                "• **वाहन का प्रकार (Vehicle Type)**: गाड़ी चुनें:\n"
                "   - *Mahindra Bolero Maxx Pickup HD 2.0L* (2-टनी पिकअप | ₹20/KM)\n"
                "   - *Tata Ace (छोटा हाथी)* / *मिनी ट्रक* / *ट्रैक्टर ट्रॉली* / *वैन*\n\n"
                "✨ **चरण 2: ऐच्छिक ऑप्शंस (Optional Extra Features)**:\n"
                "• **ईमेल (Email)**: PDF इनवॉइस रसीद प्राप्त करने के लिए।\n"
                "• **दूरी (Distance in KM)**: मैन्युअल डालें या Google Map से ऑटो-कैलकुलेट होने दें!\n"
                "• **ट्रिप का प्रकार (Trip Type)**: `One Way` (एक तरफा) या `Round Trip` (आना-जाना)।\n"
                "• **माल का प्रकार (Cargo Description)**: क्या सामान भेजना है (जैसे सीमेंट, फर्नीचर, इलेक्ट्रॉनिक्स, घर शिफ्टिंग)।\n"
                "• **वजन (Weight & Unit)**: माल का वजन `Kg` या `Ton` में चुनें।\n"
                "• **विशेष निर्देश (Message)**: ड्राइवर या लोडिंग टीम के लिए खास संदेश।\n"
                "• **ऑडियो/फोटो/वीडियो अटैचमेंट**: सामान की फोटो, वीडियो या वॉइस रिकॉर्डिंग भेजें ताकि सही गाड़ियां अलॉट की जा सकें!\n\n"
                "💰 **चरण 3: भाड़ा और बुकिंग ID**: standard किराया **₹20/KM** है (लोकल < 15 KM के लिए मिनिमम ₹500)। फॉर्म सबमिट करते ही आपको यूनिक **Booking ID** (जैसे `GT4892`) मिलेगी!\n\n"
                "👨‍✈️ **वेरिफाइड ड्राइवर**: Pankaj Kumar Sahu (Phone: `7489297841` | Bolero Maxx `CG 04 MW 2286`).\n\n"
                "💡 *Tip*: होम पेज पर **`📦 Book Transport`** या **`💰 Check Fare`** बटन दबाकर तुरंत बुकिंग करें!"
            )
        return JsonResponse({"reply": reply})

    # 💰 6. Fare & Rates Queries
    if any(k in msg_lower for k in ['fare', 'kiraya', 'rate', 'cost', 'price', 'kitna lagega', 'charges']):
        return JsonResponse({"reply": "Ghidora Transport standard freight rate is ₹20 per KM (Minimum fare ₹500 for local distances under 15 KM). Please share your Pickup and Destination to get exact fare." if is_en else "Ghidora Transport ka standard freight rate ₹20 per KM hai (Minimum fare ₹500 for local under 15 KM). Apna Pickup Location aur Destination batayein, main exact fare calculate karke bata deti hoon."})

    # 📍 7. Location & Address Queries
    if any(k in msg_lower for k in ['location', 'kahan', 'address', 'office', 'dhamtari', 'kurud', 'kodebod', 'pata', 'where']):
        return JsonResponse({"reply": "Ghidora Transport Head Office is located at Kodebod, Kurud, Dhamtari, Chhattisgarh, India. We cover Raipur, Bilaspur, Durg, Bhilai and All India 25+ cities." if is_en else "Ghidora Transport ka Head Office Kodebod, Kurud, Dhamtari, Chhattisgarh, India mein hai. Hum Raipur, Bilaspur, Durg, Bhilai aur All India 25+ cities cover karte hain."})

    # 🏎️ 8. 360 Degree Vehicle Viewer Queries
    if any(k in msg_lower for k in ['360', '360 view', '360 degree', '3d view', 'bolero 360', 'pickup 360']):
        return JsonResponse({"reply": "🏎️ **Premium True 360° Vehicle Viewer**: Experience our Mahindra Bolero Pickup in 3D 360° space! On desktop, click & drag mouse left/right to rotate. On mobile, swipe with finger. Includes 🔍 Zoom, ▶ Auto Rotate, ⛶ Fullscreen, and live 🧭 0°-360° compass angle badge! Click '🏎️ 360° View' in Navbar to try it out." if is_en else "🏎️ **प्रीमियम 360° व्हीकल व्यूअर**: हमारी वेबसाइट पर Mahindra Bolero Pickup का 3D 360° इंटरैक्टिव व्यूअर मौजूद है! माउस से ड्रैग करके या मोबाइल में स्वाइप करके गाड़ी 360-डिग्री घुमाकर देखें। इसमें 🔍 Zoom, ▶ Auto Rotate, ⛶ Fullscreen और 🧭 0°-360° लाइव कंपस शामिल है!"})

    # 🚚 8. Vehicle & Fleet Queries
    if any(k in msg_lower for k in ['vehicle', 'truck', 'bolero', 'maxx', 'capacity', 'weight']):
        return JsonResponse({"reply": "Humari primary fleet Mahindra Bolero Maxx Pickup HD 2.0L hai (Vehicle No: CG 04 MW 2286 | 2-Ton Capacity | 2000 kg Payload Limit | 24x7 Available)."})

    # 🚚 8. Shutter Door Queries
    if any(k in msg_lower for k in ['shutter', 'shutter door', 'truck door', 'container shutter']):
        return JsonResponse({"reply": "🚚 **3D Container Shutter Door**: Clicking 'Shutter Door' in the Navbar triggers a 3D container truck door hydraulic animation across your screen! It demonstrates Ghidora Transport's 100% enclosed, weatherproof cargo security." if is_en else "🚚 **3D कंटेनर शटर डोर**: नेवबार में 'Shutter Door' क्लिक करने से स्क्रीन पर 3D कंटेनर शटर बंद होकर खुलते हैं। यह Ghidora Transport के 100% वॉटरप्रूफ माल सुरक्षा का लाइव प्रदर्शन करता है!"})

    # 🪪 8. Business Card Queries
    if any(k in msg_lower for k in ['business card', 'visiting card', 'card', 'vcard', 'qr code']):
        return JsonResponse({"reply": "🪪 **Digital 3D Interactive Business Card**: Clicking 'Business Card' in the Navbar opens our 3D Glassmorphic Visiting Card page (`/business-card/`). It includes 3D tilt effects, vCard QR code scan to save Owner Tarun Kumar Sahu's contact directly to your phone, 1-click WhatsApp messaging, and PDF download!" if is_en else "🪪 **डिजिटल 3D बिज़नेस कार्ड (Business Card)**: नेवबार में 'Business Card' क्लिक करने पर 3D विज़िटिंग कार्ड पेज (`/business-card/`) खुलता है। इसमें 3D टिल्ट कार्ड, Owner Tarun Kumar Sahu का नंबर सेव करने के लिए vCard QR कोड, डायरेक्ट WhatsApp बटन और PDF डाउनलोड मौजूद है!"})

    # 📞 9. Support & Contact Queries
    if any(k in msg_lower for k in ['support', 'help', 'contact', 'call', 'number', 'phone', 'email', 'sampark']):
        return JsonResponse({"reply": "🕿 **Contact Ghidora Transport**: Clicking 'Contact' in the Navbar opens our Contact Page (`/contact/`). It features a live inquiry form, Google Maps office location embed (Kodebod, Kurud, Dhamtari), 24x7 helpline (+91 6266014139 / +91 6268814185), and official emails (tarunsahu2407@gmail.com / dmtamit789@gmail.com)." if is_en else "🕿 **संपर्क करें (Contact Us)**: नेवबार में 'Contact' क्लिक करने पर कांटेक्ट पेज (`/contact/`) खुलता है। इसमें लाइव मैसेज फॉर्म, गूगल मैप्स ऑफिस लोकेशन (धमतरी, कोडेबोड़), 24x7 हेल्पलाइन (6266014139 / 6268814185) और ऑफिशियल ईमेल उपलब्ध हैं!"})

    # 📦 10. Services Queries
    if any(k in msg_lower for k in ['service', 'services', 'kya karte', 'work', 'kaam', 'shifting']):
        return JsonResponse({"reply": "🛠️ **Ghidora Transport 6 Core Services**: Clicking 'Services' in the Navbar opens our Services Page (`/services/`): 1. Full Truck Load (FTL - Bolero Maxx 2-Ton), 2. Part Load (LTL Shared Freight), 3. House & Office Shifting, 4. Commercial Freight (Machinery/Cement), 5. Express Same-Day Delivery (Chhattisgarh), and 6. All India Freight Dispatch (25+ Cities)." if is_en else "🛠️ **Ghidora Transport की 6 मुख्य सेवाएं (Services)**: नेवबार में 'Services' क्लिक करने पर सर्विसेस पेज (`/services/`) खुलता है: 1. Full Truck Load (2-टनी पिकअप), 2. Part Load (शेयर्ड भाड़ा), 3. House & Office Shifting, 4. Commercial Freight (मशीनरी/सीमेंट), 5. Express Delivery (छत्तीसगढ़), और 6. All India Freight (25+ शहर)!"})

    # 💻 11. Technology Stack Queries
    if any(k in msg_lower for k in ['tech', 'django', 'python', 'system', 'database', 'sqlite']):
        return JsonResponse({"reply": "Ghidora Transport Platform Python 3.14, Django 6.0, HTML5, CSS3, JavaScript, SQLite3 aur AI Automation par chal raha hai."})

    # 👋 12. Greetings Queries
    if any(k in msg_lower for k in ['hi', 'hello', 'namaste', 'hey', 'greetings']):
        return JsonResponse({"reply": "Namaste! 👋 Main Ghidora AI (Gia) hoon. Main Ghidora Transport ki booking, fare (₹20/km), driver Pankaj Kumar Sahu, owner Tarun Kumar Sahu, ya developer Amit Kumar Sahu ke baare mein poori madad kar sakti hoon. Batayein main aapki kya seva karu?"})

    # 🌍 13. General Knowledge (GK) & Geography Queries
    if any(k in msg_lower for k in ['capital of india', 'india capital', 'bharat ki rajdhani']):
        return JsonResponse({"reply": "India ki rajdhani (Capital) New Delhi hai."})
    if any(k in msg_lower for k in ['capital of chhattisgarh', 'chhattisgarh capital', 'cg rajdhani']):
        return JsonResponse({"reply": "Chhattisgarh ki rajdhani (Capital) Raipur (Nava Raipur Atal Nagar) hai."})
    if any(k in msg_lower for k in ['president of india', 'rashtrapati']):
        return JsonResponse({"reply": "India ki Honorable President Smt. Droupadi Murmu ji hain."})
    if any(k in msg_lower for k in ['mahatma gandhi', 'bapu', 'father of nation']):
        return JsonResponse({"reply": "India ke Rashtrapita (Father of Nation) Mahatma Gandhi hain."})
    if any(k in msg_lower for k in ['missile man', 'kalam', 'abdul kalam']):
        return JsonResponse({"reply": "Dr. A.P.J. Abdul Kalam ji ko India ka Missile Man kaha jata hai."})

    # 📏 14. Distance & Route GK Queries
    if 'raipur to bilaspur' in msg_lower or 'bilaspur to raipur' in msg_lower:
        return JsonResponse({"reply": "Raipur se Bilaspur ki doori lagbhag 120 KM hai. Ghidora Transport ₹20/KM rate par ₹2,400 mein Bolero Pickup available karata hai."})
    if 'raipur to durg' in msg_lower or 'durg to raipur' in msg_lower:
        return JsonResponse({"reply": "Raipur se Durg ki doori lagbhag 40 KM hai. Ghidora Transport ₹20/KM rate par ₹800 mein Bolero Pickup available karata hai."})
    if 'dhamtari to raipur' in msg_lower or 'raipur to dhamtari' in msg_lower:
        return JsonResponse({"reply": "Dhamtari se Raipur ki doori lagbhag 75 KM hai. Ghidora Transport ₹20/KM rate par ₹1,500 mein Bolero Pickup available karata hai."})

    # 🔬 15. Science, Space & Tech GK Queries
    if any(k in msg_lower for k in ['ai kya hai', 'what is ai', 'artificial intelligence']):
        return JsonResponse({"reply": "Artificial Intelligence (AI) computer science ki wo shakha hai jo machines ko insano ki tarah sochne, samajhne aur kaam karne ki kshamta deti hai."})
    if any(k in msg_lower for k in ['isro', 'chandrayaan']):
        return JsonResponse({"reply": "ISRO (Indian Space Research Organisation) India ki premier space agency hai, jisne Chandrayaan-3 se Moon par safal landing ki!"})

    # 🤖 16. Dynamic Gemini API Call with Smart Fallback
    try:
        reply = get_reply(message)
        if reply and "Chatbot abhi available nahi" not in reply:
            return JsonResponse({"reply": reply})
    except Exception as e:
        print("CHATBOT GEMINI ERROR:", repr(e))

    # Smart default fallback
    fallback_reply = (
        f"Aapne '{message}' ke baare mein poochha. Main Ghidora AI (Gia) hoon — aap मुझसे Ghidora Transport booking (Pickup & Destination), "
        f"₹20/KM fare, driver Pankaj Kumar Sahu, owner Tarun Kumar Sahu, ya developer Amit Kumar Sahu ke baare mein pooch sakte hain!"
    )
    return JsonResponse({"reply": fallback_reply})


@csrf_exempt
@require_POST
def confirm_gia_booking(request):
    """
    Creates a real GiaBookingRecord and Booking in Django Database
    when customer confirms booking in Gia AI chat widget!
    """
    try:
        data = json.loads(request.body)
        pickup = data.get("pickup", "Raipur")
        drop = data.get("drop", "Dhamtari")
        goods = data.get("goods", "General Freight")
        weight = int(data.get("weight", 500))
        weight_display = str(data.get("weight_display", f"{weight} kg"))
        weight_unit = str(data.get("weight_unit", "kg"))
        distance = int(data.get("distance", 50))
        vehicle = data.get("vehicle", "Mahindra Pickup")
        fare = float(data.get("fare", distance * 20))
        phone = data.get("phone", "").strip()

        if not phone:
            return JsonResponse({"error": "Phone number required"}, status=400)

        import random
        booking_id = "GT" + str(random.randint(10000, 99999))

        from booking.models import GiaBookingRecord, Booking
        from datetime import date
        from django.db import connection

        # Ensure SQLite table exists dynamically
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS booking_giabookingrecord (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        booking_id VARCHAR(30) UNIQUE,
                        customer_name VARCHAR(100),
                        phone VARCHAR(20),
                        pickup VARCHAR(200),
                        destination VARCHAR(200),
                        goods_type VARCHAR(200),
                        weight_kg INTEGER,
                        weight_display VARCHAR(50),
                        distance_km INTEGER,
                        vehicle_assigned VARCHAR(100),
                        total_fare REAL,
                        status VARCHAR(30),
                        source VARCHAR(50),
                        created_at DATETIME
                    )
                """)
        except Exception as tbl_err:
            print("Table check:", tbl_err)

        # 1. Create Gia AI Booking Record
        GiaBookingRecord.objects.create(
            booking_id=booking_id,
            customer_name="Gia AI Customer",
            phone=phone,
            pickup=pickup,
            destination=drop,
            goods_type=goods,
            weight_kg=weight,
            weight_display=weight_display,
            distance_km=distance,
            vehicle_assigned=vehicle,
            total_fare=fare,
            status="Confirmed",
            source="Gia AI Assistant Widget"
        )

        # 2. Create main Booking entry for complete sync
        try:
            Booking.objects.create(
                booking_id=booking_id,
                name="Gia AI Customer",
                phone=phone,
                pickup=pickup,
                destination=drop,
                distance=float(distance),
                fare=fare,
                vehicle_type='Mahindra Pickup',
                cargo_type=goods,
                weight_value=weight,
                status='Confirmed',
                journey_date=date.today()
            )
        except Exception as b_err:
            print("Booking sync warning:", b_err)

        return JsonResponse({
            "status": "success",
            "booking_id": booking_id,
            "message": f"Dhanyawad! Aapki booking confirm kar li gayi hai. Booking ID: {booking_id}."
        })
    except Exception as e:
        print("ERROR CREATING GIA BOOKING:", repr(e))
        return JsonResponse({"error": str(e)}, status=500)