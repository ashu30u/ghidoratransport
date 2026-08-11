"""
Run this on a schedule (cron every 15-30 min, or Celery beat) to:
  - send reminder notifications at configured hours before the deadline
  - expire payment requests whose deadline has passed

Example cron entry (every 15 minutes):
    */15 * * * * cd /path/to/project && python manage.py send_payment_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from payments.models import PaymentRequest, PaymentStatus, PaymentSettings, NotificationType
from payments.utils import notify


class Command(BaseCommand):
    help = "Sends payment reminder notifications and expires overdue payment requests."

    def handle(self, *args, **options):
        settings_obj = PaymentSettings.get_solo()
        reminder_hours = settings_obj.reminder_hour_list() or [6, 12]
        now = timezone.now()

        pending = PaymentRequest.objects.filter(
            status=PaymentStatus.PENDING
        ).select_related("booking")

        reminded, expired = 0, 0

        for pr in pending:
            hours_until_due = (pr.due_date - now).total_seconds() / 3600

            if hours_until_due <= 0:
                pr.status = PaymentStatus.EXPIRED
                pr.save(update_fields=["status", "updated_at"])
                notify(
                    notification_type=NotificationType.BOOKING_EXPIRED,
                    message=f"Payment window for booking {pr.booking.booking_id} has "
                             f"expired. Please contact support to reinitiate payment.",
                    booking=pr.booking, payment_request=pr,
                )
                expired += 1
                continue

            for hours in reminder_hours:
                # Fire a reminder once hours_until_due crosses below the
                # configured threshold (checked within a 15-min tolerance
                # window so it fires once per scheduled run).
                if hours - 0.25 <= hours_until_due <= hours + 0.25:
                    notify(
                        notification_type=NotificationType.PAYMENT_REMINDER,
                        message=f"Reminder: Rs. {pr.amount} is due for booking "
                                 f"{pr.booking.booking_id} in about {hours} hour(s).",
                        booking=pr.booking, payment_request=pr,
                    )
                    reminded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Reminders sent: {reminded}. Payment requests expired: {expired}."
        ))
