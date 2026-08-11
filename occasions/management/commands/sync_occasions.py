from django.core.management.base import BaseCommand
from occasions.services import sync_upcoming_occasions, get_occasion_settings, dispatch_occasion_notifications
from occasions.models import Occasion
from datetime import date, datetime

class Command(BaseCommand):
    help = "Sync upcoming festivals from Google Calendar ~30 days in advance, generate AI messages, and process auto-sending."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Smart Occasions Synchronization..."))
        
        # 1. Fetch upcoming events & generate AI messages
        res = sync_upcoming_occasions()
        self.stdout.write(self.style.SUCCESS(f"Sync Completed: {res.get('imported', 0)} new occasions imported."))

        # 2. Check for auto-sending if enabled in settings
        settings_obj = get_occasion_settings()
        if settings_obj.auto_sending_enabled:
            today = date.today()
            due_occasions = Occasion.objects.filter(
                date=today,
                approval_status='approved',
                is_active=True
            ).exclude(status='sent')

            for occ in due_occasions:
                self.stdout.write(f"Dispatching scheduled notifications for: {occ.name}")
                send_res = dispatch_occasion_notifications(occ)
                self.stdout.write(self.style.SUCCESS(f"Dispatched {occ.name}: {send_res}"))

        self.stdout.write(self.style.SUCCESS("Smart Occasions sync task finished successfully."))
