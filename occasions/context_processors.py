from datetime import date
from .models import Occasion


def active_occasion(request):
    try:
        today = date.today()
        occasion = Occasion.objects.filter(
            month=today.month,
            day=today.day,
            is_active=True,
        ).first()
        return {'active_occasion': occasion}
    except Exception:
        return {'active_occasion': None}