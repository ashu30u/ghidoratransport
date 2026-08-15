from django.http import JsonResponse
from django.utils import timezone

def health_check(request):
    """
    Lightweight, public health endpoint for Render deployment & UptimeRobot monitoring.
    Returns HTTP 200 OK with status and ISO timestamp.
    No database queries or external API dependencies to ensure sub-millisecond response.
    """
    return JsonResponse({
        "status": "ok",
        "timestamp": timezone.now().isoformat()
    })
