from datetime import date

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.core.mail.message import EmailMessage
from django.conf import settings

from occasions.models import Occasion
from booking.models import Booking


class Command(BaseCommand):
    help = "Aaj ki date pe agar koi occasion match kare, to sabhi past customers ko email bhejta hai"

    def handle(self, *args, **options):
        today = date.today()
        current_year = today.year

        occasions = Occasion.objects.filter(
            month=today.month,
            day=today.day,
            is_active=True,
        ).exclude(last_sent_year=current_year)

        if not occasions.exists():
            self.stdout.write("Aaj koi occasion match nahi hua.")
            return

        emails = (
            Booking.objects
            .exclude(email__isnull=True)
            .exclude(email__exact='')
            .values_list('email', flat=True)
            .distinct()
        )
        emails = list(emails)

        if not emails:
            self.stdout.write("Koi customer email nahi mila.")
            return

        for occasion in occasions:
            subject = f"{occasion.name} Mubarak ho - Ghidora Transport"
            plain_text = occasion.message or f"Happy {occasion.name} from Ghidora Transport!"

            # HTML body - agar poster hai to <img> tag se inline dikhega
            if occasion.poster:
                html_body = f"""
                <div style="font-family: Arial, sans-serif; font-size: 15px; color: #333;">
                    <img src="cid:poster_image" style="max-width: 100%; border-radius: 8px;" />
                    <p style="margin-top: 15px; white-space: pre-line;">{plain_text}</p>
                </div>
                """
            else:
                html_body = f"""
                <div style="font-family: Arial, sans-serif; font-size: 15px; color: #333;">
                    <p style="white-space: pre-line;">{plain_text}</p>
                </div>
                """

            sent_count = 0
            for email in emails:
                try:
                    mail = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_text,  # plain text fallback
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                    )
                    mail.attach_alternative(html_body, "text/html")
                    

                    if occasion.poster:
                        from email.mime.image import MIMEImage
                        occasion.poster.open('rb')
                        img_data = occasion.poster.read()
                        occasion.poster.close()

                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', '<poster_image>')
                        img.add_header('Content-Disposition', 'inline', filename=occasion.poster.name.split('/')[-1])
                        mail.attach(img)

                    mail.send(fail_silently=False)
                    sent_count += 1
                except Exception as e:
                    self.stdout.write(f"Failed for {email}: {e}")

            occasion.last_sent_year = current_year
            occasion.save()
            self.stdout.write(f"{occasion.name}: {sent_count} customers ko email bhej diya.")