"""
chatbot/views.py

FREE AI version - Google Gemini use karta hai (koi cost nahi,
free tier ke andar). POST /api/chat/  Body: {"message": "..."}
Response: {"reply": "..."}
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

    if not message:
        return JsonResponse({"error": "Message empty hai"}, status=400)

    if len(message) > 500:
        return JsonResponse({"error": "Message bahut lamba hai"}, status=400)

    try:
        reply = get_reply(message)
    except Exception as e:
        print("CHATBOT ERROR:", repr(e))
        reply = "Kuch technical dikkat hui. Please humari support team se WhatsApp par baat karein."

    return JsonResponse({"reply": reply})