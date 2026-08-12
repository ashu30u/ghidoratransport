from datetime import date
from .models import Occasion, OccasionSettings


def active_occasion(request):
    try:
        setting = OccasionSettings.objects.first()
        if setting and hasattr(setting, 'show_on_website') and not setting.show_on_website:
            return {'active_occasion': None}

        today = date.today()
        occasion = Occasion.objects.filter(
            month=today.month,
            day=today.day,
            is_active=True,
        ).first()
        return {'active_occasion': occasion}
    except Exception:
        return {'active_occasion': None}