from datetime import date
from .models import Occasion


def active_occasion(request):
    today = date.today()
    occasion = Occasion.objects.filter(
        month=today.month,
        day=today.day,
        is_active=True,
    ).first()
    return {'active_occasion': occasion}