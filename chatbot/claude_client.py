"""
chatbot/claude_client.py

Ye module Claude API ko call karta hai "tools" ke saath.
Flow:
  1. Customer ka message + tool definitions Claude ko bhejte hain
  2. Claude decide karta hai: normal reply dena hai ya koi tool call karna hai
  3. Agar tool call hai -> hum apna Python function (services.py) run karte hain
  4. Result Claude ko wapas bhejte hain -> Claude natural Hindi/Hinglish reply banata hai
"""

import os
import json
import anthropic

from . import services

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Aap Ghidora Transport ke liye ek helpful customer support assistant hain.

Language rule: customer JIS bhasha me sawaal poochhe, usi bhasha me jawab dein —
agar customer Hindi me poochhe to Hindi/Hinglish me, agar English me poochhe to
English me, agar mix kiya to natural Hinglish me. Har reply ke andar language switch
mat karein — poore jawab me ek hi bhasha consistently use karein jab tak customer
khud switch na kare.

Fare ya booking status ke liye HAMESHA diye gaye tools use karein — khud se number
ya status kabhi mat banayein. Agar tool error return kare, customer ko politely
bataein (usi bhasha me jisme woh baat kar raha hai) aur human support (WhatsApp/phone)
suggest karein. Sensitive info (driver contact) sirf verified booking ke liye dein."""

TOOLS = [
    {
        "name": "calculate_fare",
        "description": "Do jagah ke beech estimated fare aur distance calculate karta hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Pickup location"},
                "destination": {"type": "string", "description": "Drop location"},
                "vehicle_type": {"type": "string", "description": "Optional. e.g. Mahindra Pickup, Tata Ace, Mini Truck, Mini Bus"},
            },
            "required": ["source", "destination"],
        },
    },
    {
        "name": "get_booking_status",
        "description": "Booking ID se current status, driver, aur vehicle details deta hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "e.g. GT00025"},
            },
            "required": ["booking_id"],
        },
    },
    {
        "name": "get_driver_contact",
        "description": "Verified booking ke liye driver ka phone number deta hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
            },
            "required": ["booking_id"],
        },
    },
    {
        "name": "get_services",
        "description": "Ghidora Transport ki saari available services ki list deta hai.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

TOOL_FUNCTIONS = {
    "calculate_fare": lambda i: services.calculate_fare(i["source"], i["destination"], i.get("vehicle_type")),
    "get_booking_status": lambda i: services.get_booking_status(i["booking_id"]),
    "get_driver_contact": lambda i: services.get_driver_contact(i["booking_id"]),
    "get_services": lambda i: services.get_services(),
}


def run_chat(message: str, conversation_history: list = None) -> dict:
    """
    message: customer ka naya message
    conversation_history: pichle messages ki list [{"role": "user"/"assistant", "content": "..."}]

    Returns: {"reply": str, "history": updated_history}
    """
    history = conversation_history or []
    messages = history + [{"role": "user", "content": message}]

    # Claude ko tool-use loop me call karo (max 3 round-trips safety ke liye)
    for _ in range(3):
        response = client.messages.create(
            model=MODEL,
            max_tokens=800,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            # Normal text reply mil gaya
            reply_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            messages.append({"role": "assistant", "content": response.content})
            return {"reply": reply_text, "history": messages}

        # Tool call handle karo
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                func = TOOL_FUNCTIONS.get(block.name)
                result = func(block.input) if func else {"error": "Unknown tool"}
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

        messages.append({"role": "user", "content": tool_results})

    return {
        "reply": "Maaf kijiye, abhi jawab dene me dikkat aa rahi hai. Please humari support team se WhatsApp par baat karein.",
        "history": messages,
    }
