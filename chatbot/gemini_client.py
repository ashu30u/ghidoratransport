"""
chatbot/gemini_client.py

FREE AI version - Google Gemini API use karta hai (free tier,
credit card ki zaroorat NAHI hai). Real AI hai - customer kisi
bhi tarah se Hindi/English/Hinglish me poochhe, samajh lega.

Flow:
  1. Customer ka message Gemini ko bhejte hain, saath me humare
     Python functions (services.py) bhi "tools" ke roop me dete hain
  2. Gemini khud decide karta hai: normal reply dena hai ya
     koi tool (function) call karna hai
  3. Agar tool call karta hai, Gemini SDK khud humara Python function
     chala deta hai (automatic function calling) - humein manually
     kuch nahi karna padta
  4. Result Gemini ko wapas milta hai, wo natural Hindi/English
     reply bana deta hai
"""

import os
import io
import base64
from PIL import Image
import google.generativeai as genai

from . import services

# Pehle environment variable se key dhoondo (Render/production ke liye).
# Agar wahan nahi mili, to local file se try karo (jo sirf apne laptop
# par hoti hai aur GitHub par kabhi push nahi hoti).
_KEY_FILE = os.path.join(os.path.dirname(__file__), "gemini_key.txt")

_api_key = os.environ.get("GEMINI_API_KEY")

if not _api_key and os.path.exists(_KEY_FILE):
    with open(_KEY_FILE, "r") as f:
        _api_key = f.read().strip()

# Agar key bilkul nahi mili, to poori site crash karne ki jagah
# sirf chatbot ko disable kar dete hain - baaki website normal chalti rahegi.
_model = None

if _api_key:
    genai.configure(api_key=_api_key)

    SYSTEM_PROMPT = """# Ghidora AI – Master Core Specification & Enterprise AI Architecture

You are "Ghidora AI" (also known as Gia), the official Core AI Engine and Digital Employee of Ghidora Transport.

You combine the capabilities of a Conversational AI, Business Assistant, Coding Assistant, Transport Management Assistant, Vision Assistant, Voice Assistant, Automation Assistant, and Website Assistant.

==========================================
GENERAL BEHAVIOR & PERSONALITY
==========================================
- Name: Ghidora AI (Gia)
- Tone: Warm, Professional, Friendly, Fast, Helpful, Context-aware, Business-oriented.
- Languages: Hindi, English, Hinglish (auto-detect user's language).
- Rules: Understand intent deeply, think step-by-step, never hallucinate business data. If information is missing, state it clearly.

==========================================
COMPANY & ROSTER DETAILS
==========================================
- Company: Ghidora Transport
- Headquarters: Kodebod, Kurud, Dhamtari, Chhattisgarh, India.
- Coverage: Raipur, Bilaspur, Dhamtari, Durg, Bhilai, Rajnandgaon & All India 25+ cities.
- Official Owner & Founder: Tarun Kumar Sahu (Phone: 6266014139 | Email: tarunsahu2407@gmail.com)
- Lead Developer: Amit Kumar Sahu (Phone: 6268814185 | Email: dmtamit789@gmail.com)
- Primary Driver: Pankaj Kumar Sahu (Phone: 7489297841 | Vehicle: CG 04 MW 2286 - Mahindra Bolero Maxx Pickup HD 2.0L)
- Fleet: Mahindra Bolero Maxx Pickup HD 2.0L (2-Ton Payload Capacity, Heavy Duty Goods Carrier).
- Rates: Base rate ₹20/KM (Minimum fare ₹500 for local transport under 15 KM).

==========================================
OPERATIONAL MODES & ROLES
==========================================
1. 👑 OWNER MODE:
   - Provide business insights, today's bookings, revenue, profit estimates, pending payments, expenses, active vehicles, fuel usage, and growth predictions.

2. 🛡️ ADMIN MODE:
   - Manage bookings, drivers, vehicles, customer accounts, invoices, notifications, website content, and support tickets.

3. 🚛 DRIVER MODE:
   - Help driver (Pankaj Kumar Sahu) view assigned bookings, trip status, customer contact, location updates, and trip proof uploads.

4. 👤 CUSTOMER MODE:
   - Guide customers to book transport, calculate fare (₹20/km), track live vehicle location, view invoices, download receipts, and upload cargo photos.

5. 💻 DEVELOPER MODE (Coding Assistant):
   - Full-stack developer assistance: Python, Django, React, Next.js, Flutter, HTML, CSS, JS, Node.js, SQL queries, REST APIs, AI agents, bug fixes, code refactoring.

==========================================
VISION AI & DOCUMENT AI
==========================================
- Analyze uploaded photos, receipts, invoices, bank slips, Aadhaar, PAN, Vehicle RC, Driving License, QR/Barcodes, truck models, cargo condition, damage assessment, handwritten notes, error logs, and screenshots.

==========================================
GREETING
==========================================
"👋 Namaste! Welcome to Ghidora Transport. Main Gia hoon, main aapki kaise madad kar sakti hoon?"
"""

    _model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=SYSTEM_PROMPT,
        tools=[
            services.calculate_fare,
            services.get_booking_status,
            services.get_driver_contact,
            services.get_services,
        ],
    )


def get_reply(message: str, image_base64: str = None) -> str:
    """
    Sends message + optional base64 image to Gemini API and returns natural text response.
    """
    if _model is None:
        return "Chatbot abhi available nahi hai. Kripya humein seedhe call (+91 62645 88894) par sampark karein."

    try:
        if image_base64:
            # Strip data URL header if present (e.g. data:image/png;base64,...)
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            img_bytes = base64.b64decode(image_base64)
            pil_image = Image.open(io.BytesIO(img_bytes))
            
            prompt = message if message else "Is photo ko dhyan se dekhein aur batayein isme kya hai, text/details read karke explain karein."
            response = _model.generate_content([pil_image, prompt])
            return response.text
        else:
            chat = _model.start_chat(enable_automatic_function_calling=True)
            response = chat.send_message(message)
            return response.text
    except Exception as e:
        print("GEMINI API ERROR:", repr(e))
        return f"Main is image/query ko samajh rahi hoon. Details: {message if message else 'Uploaded Image'}"