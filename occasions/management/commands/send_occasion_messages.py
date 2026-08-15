from datetime import date
from django.core.management.base import BaseCommand
from occasions.models import Occasion
from occasions.services import dispatch_occasion_notifications


class Command(BaseCommand):
    help = "Aaj ki date pe agar koi occasion match kare, to sabhi past customers ko email bhejta hai"

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force send even if not approved or already sent')

    def handle(self, *args, **options):
        force = options.get('force', False)
        today = date.today()
        current_year = today.year

        occasions = Occasion.objects.filter(
            month=today.month,
            day=today.day,
            is_active=True,
        )
        if not force:
            occasions = occasions.exclude(last_sent_year=current_year)

        if not occasions.exists():
            self.stdout.write("Aaj koi active occasion match nahi hua.")
            return

        for occasion in occasions:
            res = dispatch_occasion_notifications(occasion, force=force)
            sent_count = res.get('sent', 0)
            status_msg = res.get('status') or res.get('error')
            self.stdout.write(f"{occasion.name}: {sent_count} customers ko email bhej diya ({status_msg}).")