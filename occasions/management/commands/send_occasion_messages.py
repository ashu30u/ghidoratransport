from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone
from occasions.models import Occasion
from occasions.services import check_and_send_due_occasions, dispatch_occasion_notifications


class Command(BaseCommand):
    help = "Checks scheduled occasions and today's occasions, and sends greeting emails to customers"

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force send even if not approved or already sent')

    def handle(self, *args, **options):
        force = options.get('force', False)
        today = date.today()
        now = timezone.now()

        self.stdout.write(f"[SCHEDULE] Checking scheduled occasions for {today.strftime('%Y-%m-%d')} at {timezone.localtime(now).strftime('%I:%M:%S %p')}...")

        res = check_and_send_due_occasions(force=force)
        total_due = res.get('total_due', 0)
        dispatched = res.get('dispatched', [])

        if not dispatched:
            # Check if there are any approved occasions scheduled for later today
            later_today = Occasion.objects.filter(
                approval_status='approved',
                is_active=True,
                scheduled_at__date=today,
                scheduled_at__gt=now
            )
            if later_today.exists():
                for occ in later_today:
                    local_t = timezone.localtime(occ.scheduled_at).strftime('%I:%M %p')
                    self.stdout.write(self.style.WARNING(f"[WAITING] '{occ.name}' is scheduled for later today at {local_t}."))
            else:
                self.stdout.write("Abhi koi due occasion send karne ke liye nahi hai.")
            return

        for item in dispatched:
            name = item.get('name')
            sent = item.get('sent', 0)
            status_text = item.get('status')
            if sent > 0:
                self.stdout.write(self.style.SUCCESS(f"[SUCCESS] {name}: {sent} customers ko email bhej diya ({status_text})."))
            else:
                self.stdout.write(self.style.ERROR(f"[FAILED] {name}: Send nahi ho paya ({status_text})."))
