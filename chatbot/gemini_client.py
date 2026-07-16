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

    SYSTEM_PROMPT = """Aap Ghidora Transport ke liye ek helpful customer support assistant hain.

Language rule: customer JIS bhasha me sawaal poochhe, usi bhasha me jawab dein -
Hindi poocha to Hindi/Hinglish me, English poocha to English me.

Fare ya booking status ke liye HAMESHA diye gaye tools/functions use karein -
khud se number ya status kabhi mat banayein. Agar customer vehicle type na
bataye, function khud ek default vehicle se estimate dega - customer ko
bata dein ki vehicle badalne se fare alag ho sakta hai. Driver ka contact
sirf tabhi dein jab booking ID valid ho. Reply short aur friendly rakhein."""

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


def get_reply(message: str) -> str:
    """
    Ek customer message leta hai, Gemini ko bhejta hai (jo zaroorat
    padne par khud services.py ke functions call kar lega), aur
    final natural-language reply string return karta hai.

    NOTE: Ye stateless hai (har message independent) - taaki
    frontend/backend dono simple rahein. Zyada complex multi-turn
    conversations ke liye baad me history add ki ja sakti hai.
    """
    if _model is None:
        return "Chatbot abhi available nahi hai. Kripya humein seedhe call/WhatsApp par sampark karein."

    chat = _model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(message)
    return response.text