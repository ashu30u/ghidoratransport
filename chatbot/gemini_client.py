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

# Key ko environment variable ki jagah ek simple file se padhte hain -
# isse har naye terminal me dobara set karne ka jhanjhat khatam ho jata hai.
_KEY_FILE = os.path.join(os.path.dirname(__file__), "gemini_key.txt")

with open(_KEY_FILE, "r") as f:
    _api_key = f.read().strip()

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
    chat = _model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(message)
    return response.text