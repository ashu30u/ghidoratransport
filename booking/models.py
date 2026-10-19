import logging
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
import random

logger = logging.getLogger(__name__)


class Booking(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    DISTANCE_SOURCE_CHOICES = [
        ('Google Generated', 'Google Generated'),
        ('Google Maps Route', 'Google Maps Route'),
        ('Manual Entered', 'Manual Entered'),
    ]

    VEHICLE_CHOICES = [
        ('Mahindra Pickup', 'Mahindra Pickup'),
        ('Mahindra Bolero', 'Mahindra Bolero'),
        ('Mahindra Cruiser', 'Mahindra Cruiser'),
        ('Magic', 'Mahindra Jeeto Magic'),
        ('Van', 'Van'),
        ('Mini Bus', 'Mini Bus'),
        ('Tata Ace', 'Tata Ace'),
        ('Mini Truck', 'Mini Truck'),
        ('Tractor Trolley', 'Tractor Trolley'),
    ]

    WEIGHT_UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('ton', 'Ton'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    pickup = models.CharField(max_length=300)
    destination = models.CharField(max_length=300)

    pickup_lat = models.FloatField(blank=True, null=True, verbose_name="Pickup Latitude")
    pickup_lng = models.FloatField(blank=True, null=True, verbose_name="Pickup Longitude")
    destination_lat = models.FloatField(blank=True, null=True, verbose_name="Destination Latitude")
    destination_lng = models.FloatField(blank=True, null=True, verbose_name="Destination Longitude")
    duration_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="Route Duration")

    distance = models.FloatField()

    distance_source = models.CharField(
        max_length=50,
        choices=DISTANCE_SOURCE_CHOICES,
        default='Manual Entered'
    )

    FARE_TYPE_CHOICES = [
        ('Predefined Route Fare', 'Predefined Route Fare'),
        ('Distance Based Fare', 'Distance Based Fare'),
        ('Manual/Other', 'Manual/Other'),
    ]

    fare = models.FloatField()

    fare_type = models.CharField(
        max_length=50,
        choices=FARE_TYPE_CHOICES,
        default='Distance Based Fare',
        help_text="Fare calculation method used for this booking"
    )

    toll_charges = models.FloatField(default=0, blank=True, null=True)
    parking_charges = models.FloatField(default=0, blank=True, null=True)

    toll_screenshot = models.ImageField(
        upload_to='toll_screenshots/',
        blank=True,
        null=True
    )

    booking_id = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    vehicle_type = models.CharField(
        max_length=30,
        choices=VEHICLE_CHOICES,
        default='Mahindra Pickup'
    )

    assigned_driver = models.ForeignKey(
        'drivers.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bookings'
    )

    trip_type = models.CharField(
        max_length=20,
        default='One Way'
    )

    # ============================================================
    # Cargo details (customer kya bhejna chahta hai, kitna)
    # ============================================================
    cargo_type = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Customer kya transport karwana chahta hai"
    )

    weight_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    weight_unit = models.CharField(
        max_length=5,
        choices=WEIGHT_UNIT_CHOICES,
        default='kg'
    )

    message = models.TextField(
        blank=True,
        null=True,
        help_text="Customer ka free-text message"
    )

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending / Unpaid'),
        ('Paid', 'Paid (Cash / Online)'),
        ('Partial', 'Partially Paid'),
        ('Failed', 'Failed / Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending',
        help_text="Admin can manually update payment status (e.g. Paid via Cash to Owner/Driver)"
    )

    booking_date = models.DateTimeField(
        auto_now_add=True
    )

    journey_date = models.DateField()

    def save(self, *args, **kwargs):

        if not self.booking_id:
            self.booking_id = "GT" + str(
                random.randint(1000, 9999)
            )

        super().save(*args, **kwargs)

    @property
    def total_fare(self):
        toll = self.toll_charges or 0
        parking = self.parking_charges or 0
        return self.fare + toll + parking

    def __str__(self):
        return (
            self.booking_id
            if self.booking_id
            else self.name
        )


# ============================================================
# Voice message / Photo / Video jo customer bhejta hai
# ============================================================
class BookingAttachment(models.Model):

    ATTACHMENT_TYPE_CHOICES = [
        ('voice', 'Voice Message'),
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    attachment_type = models.CharField(
        max_length=10,
        choices=ATTACHMENT_TYPE_CHOICES
    )

    file = models.FileField(
        upload_to='booking_attachments/%Y/%m/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.attachment_type} - {self.booking.booking_id}"


class Review(models.Model):

    RATING_CHOICES = [
        (1, "⭐"),
        (2, "⭐⭐"),
        (3, "⭐⭐⭐"),
        (4, "⭐⭐⭐⭐"),
        (5, "⭐⭐⭐⭐⭐"),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_reviews'
    )

    guest_name = models.CharField(max_length=100, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    guest_phone = models.CharField(max_length=15, blank=True, null=True)

    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5
    )

    comment = models.TextField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)

    service_used = models.CharField(max_length=100, blank=True, null=True, default='Full Truck Transport')
    photo = models.ImageField(upload_to='review_photos/%Y/%m/', blank=True, null=True)

    is_approved = models.BooleanField(default=True, help_text="Approved by Admin to display on site")
    is_verified = models.BooleanField(default=False, help_text="Verified Customer Badge")
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def display_name(self):
        if self.booking and self.booking.name:
            return self.booking.name
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.guest_name or "Ghidora Customer"

    def __str__(self):
        return f"{self.display_name} - {self.rating}⭐ ({'Approved' if self.is_approved else 'Pending'})"


@receiver([post_save, post_delete], sender=Review)
def _clear_home_reviews_cache(sender, instance, **kwargs):
    try:
        cache.delete("home_reviews_summary_data")
    except Exception:
        pass


# ============================================================
# Review Social Interactions (Likes, Comments, Shares in DB)
# ============================================================
class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like on Review #{self.review.id}"


class ReviewComment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user_name} on Review #{self.review.id}"


class ReviewShare(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    platform = models.CharField(max_length=50, default='whatsapp')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Share ({self.platform}) on Review #{self.review.id}"



# ============================================================
# Contact Us page ke messages (customer name/phone/message bhejta hai)
# ============================================================
class ContactMessage(models.Model):

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.subject or 'No subject'}"


# ============================================================
# EMAIL RECEIPT FLOW -- signals
# ============================================================

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


@receiver(pre_save, sender=Booking)
def _track_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = Booking.objects.get(pk=instance.pk).status
        except Booking.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


def _send_admin_new_booking_alert_worker(booking_id):
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        instance = Booking.objects.filter(pk=booking_id).first()
        if not instance:
            return
        subject = f"🚨 NEW BOOKING RECEIVED #{instance.booking_id} - {instance.name}"
        message = f"""New Booking Received on Ghidora Transport Live Site!

Booking ID   : {instance.booking_id}
Customer Name: {instance.name}
Phone        : {instance.phone}
Email        : {instance.email or 'N/A'}

Pickup       : {instance.pickup}
Destination  : {instance.destination}
Journey Date : {instance.journey_date}

Distance     : {instance.distance} KM
Vehicle      : {instance.vehicle_type} ({instance.trip_type})
Total Fare   : ₹{instance.fare} ({getattr(instance, 'fare_type', 'Calculated Fare')})
Status       : {instance.status}

Cargo Type   : {instance.cargo_type or 'Standard'}
Weight       : {instance.weight_value or ''} {instance.weight_unit or ''}
Message      : {instance.message or 'None'}

Please check Live Admin Panel: https://ghidoratransport.onrender.com/admin/
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['ghidoratransport@gmail.com'],
            fail_silently=True
        )
        logger.info("Admin new booking alert email sent for #%s", instance.booking_id)
    except Exception as e:
        logger.warning("Admin email notification failed: %s", e)



def _send_customer_booking_confirmation_worker(booking_id):
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    try:
        instance = Booking.objects.filter(pk=booking_id).first()
        if not instance:
            return

        customer_email = (instance.email or '').strip()
        if not customer_email and instance.user and instance.user.email:
            customer_email = instance.user.email.strip()

        if not customer_email:
            logger.info("No customer email found for booking #%s. Skipping customer confirmation email.", getattr(instance, 'booking_id', booking_id))
            return

        subject = f"🚚 Booking Confirmation #{instance.booking_id} — Ghidora Transport"

        plain_text = f"""Dear {instance.name},

Thank you for booking with Ghidora Transport Logistics!
Your booking request has been successfully received and recorded in our system.

=======================================================
BOOKING SUMMARY
=======================================================
Booking ID   : #{instance.booking_id}
Customer Name: {instance.name}
Phone        : {instance.phone}
Route        : {instance.pickup} ➔ {instance.destination}
Journey Date : {instance.journey_date}
Vehicle Type : {instance.vehicle_type}
Trip Type    : {instance.trip_type}
Distance     : {instance.distance} KM
Total Fare   : ₹{instance.fare} ({getattr(instance, 'fare_type', 'Calculated Fare')})
Status       : {instance.status}
Cargo Type   : {instance.cargo_type or 'General Goods'}
Weight       : {instance.weight_value or 'Standard'} {instance.weight_unit or ''}

=======================================================
LIVE TRACKING & SUPPORT
=======================================================
Track your trip status live here:
https://ghidoratransport.onrender.com/track/

Helpline Numbers:
📞 +91 7489297841 | +91 6266014139
✉️ Email: ghidoratransport@gmail.com
🌐 Website: https://ghidoratransport.onrender.com

Warm regards,
Ghidora Transport Logistics
Kodebod, Kurud, Dhamtari, Chhattisgarh
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Booking Confirmation - Ghidora Transport</title>
</head>
<body style="margin: 0; padding: 20px 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; color: #1e293b;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
    <!-- Header -->
    <tr>
      <td style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 28px 24px; text-align: center;">
        <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: 0.5px;">GHIDORA TRANSPORT</h1>
        <p style="margin: 6px 0 0; color: #93c5fd; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Logistics & Commercial Goods Transport</p>
      </td>
    </tr>

    <!-- Status Banner -->
    <tr>
      <td style="background-color: #ecfdf5; border-bottom: 2px solid #a7f3d0; padding: 14px 24px; text-align: center;">
        <span style="display: inline-block; background-color: #10b981; color: #ffffff; font-size: 12px; font-weight: 700; text-transform: uppercase; padding: 4px 12px; border-radius: 9999px; letter-spacing: 0.5px; margin-bottom: 4px;">✔ Booking Received</span>
        <h2 style="margin: 4px 0 0; font-size: 18px; color: #065f46; font-weight: 700;">Booking Confirmed!</h2>
      </td>
    </tr>

    <!-- Body -->
    <tr>
      <td style="padding: 24px;">
        <p style="margin: 0 0 16px; font-size: 15px; line-height: 1.5; color: #334155;">
          Dear <strong>{instance.name}</strong>,<br>
          Thank you for choosing <strong>Ghidora Transport</strong>! We have received your booking request and our team is preparing for your transport.
        </p>

        <!-- Booking ID Card -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px;">
          <tr>
            <td style="padding: 14px 18px;">
              <span style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase;">Your Booking ID</span><br>
              <strong style="font-size: 22px; color: #2563eb; letter-spacing: 0.5px;">#{instance.booking_id}</strong>
            </td>
            <td style="padding: 14px 18px; text-align: right;">
              <span style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase;">Total Fare</span><br>
              <strong style="font-size: 22px; color: #059669;">₹{instance.fare}</strong>
            </td>
          </tr>
        </table>

        <!-- Details Table -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; margin-bottom: 24px; font-size: 14px;">
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 0; color: #64748b; font-weight: 600; width: 38%;">Pickup Location:</td>
            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{instance.pickup}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Destination:</td>
            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{instance.destination}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Journey Date:</td>
            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{instance.journey_date}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Vehicle:</td>
            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{instance.vehicle_type} ({instance.trip_type})</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Total Distance:</td>
            <td style="padding: 10px 0; color: #0f172a;">{instance.distance} KM</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Cargo & Weight:</td>
            <td style="padding: 10px 0; color: #0f172a;">{instance.cargo_type or 'General Cargo'} ({instance.weight_value or 'Standard'} {instance.weight_unit or ''})</td>
          </tr>
          <tr>
            <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Status:</td>
            <td style="padding: 10px 0; color: #2563eb; font-weight: 700;">{instance.status}</td>
          </tr>
        </table>

        <!-- Button -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px;">
          <tr>
            <td style="text-align: center;">
              <a href="https://ghidoratransport.onrender.com/track/" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; padding: 12px 28px; border-radius: 8px; box-shadow: 0 2px 8px rgba(37,99,235,0.3);">
                🚚 Track Booking Online
              </a>
            </td>
          </tr>
        </table>

        <!-- Help box -->
        <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 12px 16px; border-radius: 4px; font-size: 13px; color: #475569; line-height: 1.5;">
          <strong>Need immediate help or vehicle updates?</strong><br>
          Call our support team: <strong>+91 7489297841</strong> / <strong>+91 6266014139</strong><br>
          Email: <a href="mailto:ghidoratransport@gmail.com" style="color: #2563eb;">ghidoratransport@gmail.com</a>
        </div>
      </td>
    </tr>

    <!-- Footer -->
    <tr>
      <td style="background-color: #0f172a; padding: 20px 24px; text-align: center; color: #94a3b8; font-size: 12px; line-height: 1.5;">
        <strong style="color: #ffffff;">Ghidora Transport Logistics</strong><br>
        Kodebod, Kurud, Dhamtari, Chhattisgarh, India<br>
        Website: <a href="https://ghidoratransport.onrender.com" style="color: #60a5fa; text-decoration: none;">https://ghidoratransport.onrender.com</a>
      </td>
    </tr>
  </table>
</body>
</html>
"""

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email],
        )
        msg.attach_alternative(html_content, "text/html")

        # Optional: Attach Receipt PDF if available
        try:
            from .utils import generate_receipt_pdf
            pdf_buffer = generate_receipt_pdf(instance)
            if pdf_buffer:
                msg.attach(
                    f"Booking_Receipt_{instance.booking_id}.pdf",
                    pdf_buffer.getvalue(),
                    "application/pdf"
                )
        except Exception as pdf_err:
            logger.warning("Could not attach receipt PDF to customer confirmation: %s", pdf_err)

        msg.send(fail_silently=False)
        logger.info("Customer booking confirmation email sent to %s for #%s", customer_email, instance.booking_id)
        print(f"[OK] Customer confirmation email sent to {customer_email} for #{instance.booking_id}")
    except Exception as e:
        logger.error("Customer booking confirmation email failed for booking %s: %s", booking_id, e)
        print(f"[ERROR] Customer booking confirmation email failed for booking {booking_id}: {e}")


@receiver(post_save, sender=Booking)
def _send_booking_notifications(sender, instance, created, **kwargs):
    if created:
        import threading
        # 1. Admin Alert
        threading.Thread(
            target=_send_admin_new_booking_alert_worker,
            args=(instance.pk,),
            daemon=True
        ).start()
        # 2. Customer Confirmation Email
        threading.Thread(
            target=_send_customer_booking_confirmation_worker,
            args=(instance.pk,),
            daemon=True
        ).start()


def _send_completion_email_worker(booking_id):
    from .utils import generate_receipt_pdf
    from django.core.mail import EmailMessage
    from django.conf import settings
    try:
        instance = Booking.objects.filter(pk=booking_id).first()
        if not instance or not instance.email:
            return

        pdf_buffer = generate_receipt_pdf(instance)

        subject = "🚚 Booking Confirmation - Ghidora Transport"
        body = f"""Dear {instance.name},

Thank you for choosing Ghidora Transport.

Your booking has been completed successfully.

Booking ID : {instance.booking_id}
Pickup : {instance.pickup}
Destination : {instance.destination}
Journey Date : {instance.journey_date}
Vehicle : {instance.vehicle_type}

Please find your receipt attached.

Thank You.
Ghidora Transport
"""
        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        mail.attach(
            f"Receipt_{instance.booking_id}.pdf",
            pdf_buffer.getvalue(),
            "application/pdf"
        )
        mail.send(fail_silently=False)
        logger.info("Completion receipt email sent to %s for #%s", instance.email, instance.booking_id)
        print(f"[OK] Completion receipt email sent to {instance.email} for #{instance.booking_id}")

    except Exception as e:
        logger.error("Completion email send failed for booking %s: %s", booking_id, e)
        print(f"[ERROR] Completion email send failed for booking {booking_id}: {e}")


@receiver(post_save, sender=Booking)
def _send_email_on_completion(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    should_send = (created and instance.status == 'Completed') or (not created and instance.status == 'Completed' and previous_status != 'Completed')
    if should_send:
        if instance.email and instance.email.strip():
            import threading
            threading.Thread(
                target=_send_completion_email_worker,
                args=(instance.pk,),
                daemon=True
            ).start()


class GiaBookingRecord(models.Model):
    booking_id = models.CharField(max_length=30, unique=True)
    customer_name = models.CharField(max_length=100, default="Gia AI Customer")
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    pickup = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    goods_type = models.CharField(max_length=200, blank=True, null=True)
    weight_kg = models.IntegerField(default=500)
    weight_display = models.CharField(max_length=50, default="500 kg")
    distance_km = models.IntegerField(default=50)
    vehicle_assigned = models.CharField(max_length=100, default="Mahindra Pickup")
    total_fare = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, default="Confirmed")
    source = models.CharField(max_length=50, default="Gia AI Assistant")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gia AI Booking Record"
        verbose_name_plural = "Gia AI Booking Records"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_id} | {self.goods_type} ({self.weight_display}) | {self.pickup} -> {self.destination} (₹{self.total_fare})"


class PredefinedRouteFare(models.Model):
    from_location = models.CharField(max_length=100, help_text="Pickup location name (e.g., Dhamtari)")
    to_location = models.CharField(max_length=100, help_text="Destination location name (e.g., Raipur)")
    fixed_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Single Trip Fare (One Way ₹)",
        help_text="Single trip / One-way fixed route fare in ₹"
    )
    double_trip_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Double Trip Fare (Round Trip ₹)",
        help_text="Double trip / Round trip fixed route fare in ₹ (leave blank to auto-double single trip fare)"
    )
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Route Distance (KM)",
        help_text="Optional distance in KM for this route (e.g. 49.5). If set, this distance will be automatically filled for bookings."
    )
    is_active = models.BooleanField(default=True, verbose_name="Active / Inactive")
    same_direction_both = models.BooleanField(
        default=False,
        verbose_name="Same fare for both directions",
        help_text="If enabled, this fare applies for reverse direction (To -> From) as well."
    )
    description = models.TextField(blank=True, null=True, help_text="Optional note/description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Predefined Route Fare"
        verbose_name_plural = "Predefined Route Fares"
        ordering = ['from_location', 'to_location']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        from_clean = (self.from_location or '').strip().lower()
        to_clean = (self.to_location or '').strip().lower()

        if from_clean and to_clean and from_clean == to_clean:
            raise ValidationError("From Location and To Location cannot be the same.")

        if self.fixed_fare is not None and self.fixed_fare <= 0:
            raise ValidationError("Single Trip Fare must be greater than 0.")

        if self.double_trip_fare is not None and self.double_trip_fare <= 0:
            raise ValidationError("Double Trip Fare must be greater than 0.")

        if self.distance_km is not None and self.distance_km <= 0:
            raise ValidationError("Route Distance (KM) must be greater than 0.")

        if from_clean and to_clean:
            qs = PredefinedRouteFare.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            for route in qs:
                rf_from = route.from_location.strip().lower()
                rf_to = route.to_location.strip().lower()

                # Case 1: Exact route match
                if rf_from == from_clean and rf_to == to_clean:
                    raise ValidationError("This route fare already exists. Please edit the existing route.")

                # Case 2: Reverse direction match when same_direction_both is active
                if self.same_direction_both or route.same_direction_both:
                    if rf_from == to_clean and rf_to == from_clean:
                        raise ValidationError("This route fare already exists in the reverse direction with 'Same fare for both directions' enabled. Please edit the existing route.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_fare_for_trip_type(self, trip_type):
        """
        Returns calculated fare for given trip_type ('One Way' or 'Round Trip').
        """
        if trip_type == 'Round Trip':
            if self.double_trip_fare is not None and self.double_trip_fare > 0:
                return float(self.double_trip_fare)
            return float(self.fixed_fare) * 2
        return float(self.fixed_fare)

    def __str__(self):
        dir_str = "⇄" if self.same_direction_both else "➔"
        dt_str = f" | Round: ₹{self.double_trip_fare:,.0f}" if self.double_trip_fare else ""
        return f"{self.from_location} {dir_str} {self.to_location}: One-Way ₹{self.fixed_fare:,.0f}{dt_str} ({'Active' if self.is_active else 'Inactive'})"


class PredefinedRouteDistance(models.Model):
    from_location = models.CharField(max_length=100, help_text="Pickup location name (e.g., Kodebod)")
    to_location = models.CharField(max_length=100, help_text="Destination location name (e.g., Raipur)")
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Distance (KM)",
        help_text="Fixed route distance in KM (e.g., 49.5)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active / Inactive")
    same_direction_both = models.BooleanField(
        default=True,
        verbose_name="Same distance for both directions",
        help_text="If enabled, this distance applies for reverse direction (To -> From) as well."
    )
    description = models.TextField(blank=True, null=True, help_text="Optional note/description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Predefined Route Distance"
        verbose_name_plural = "Predefined Route Distances"
        ordering = ['from_location', 'to_location']

    def clean(self):
        from django.core.exceptions import ValidationError

        from_clean = (self.from_location or '').strip().lower()
        to_clean = (self.to_location or '').strip().lower()

        if from_clean and to_clean and from_clean == to_clean:
            raise ValidationError("From Location and To Location cannot be the same.")

        if self.distance_km is not None and self.distance_km <= 0:
            raise ValidationError("Distance (KM) must be greater than 0.")

        if from_clean and to_clean:
            qs = PredefinedRouteDistance.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            for route in qs:
                rf_from = route.from_location.strip().lower()
                rf_to = route.to_location.strip().lower()

                # Case 1: Exact route match
                if rf_from == from_clean and rf_to == to_clean:
                    raise ValidationError("This route distance already exists. Please edit the existing record.")

                # Case 2: Reverse direction match when same_direction_both is active
                if self.same_direction_both or route.same_direction_both:
                    if rf_from == to_clean and rf_to == from_clean:
                        raise ValidationError("This route distance already exists in the reverse direction with 'Same distance for both directions' enabled. Please edit the existing record.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        dir_str = "⇄" if self.same_direction_both else "➔"
        return f"{self.from_location} {dir_str} {self.to_location}: {self.distance_km} KM ({'Active' if self.is_active else 'Inactive'})"


# ============================================================
# Review System Publishing Configuration
# ============================================================
class ReviewSetting(models.Model):
    """
    Global configuration for customer reviews publishing:
    - auto_approve_reviews = True: Customer reviews appear instantly on the website.
    - auto_approve_reviews = False: Reviews require Admin approval (Manual Verification Mode).
    """
    auto_approve_reviews = models.BooleanField(
        default=True,
        verbose_name="Auto-Publish Reviews (Automatic Mode)",
        help_text="If ON: Reviews submitted by customers appear on the website instantly. If OFF: Reviews require Admin approval (Manual Mode)."
    )
    auto_verify_logged_in = models.BooleanField(
        default=True,
        verbose_name="Auto-Verify Registered Customers",
        help_text="If ON: Reviews submitted by logged-in users receive the Verified Customer badge automatically."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review System Setting"
        verbose_name_plural = "Review System Settings"

    def __str__(self):
        mode = "🟢 AUTOMATIC (Instant Publish)" if self.auto_approve_reviews else "🛡️ MANUAL (Admin Verification Required)"
        return f"Review Mode: {mode}"

    @classmethod
    def get_settings(cls):
        try:
            obj, _ = cls.objects.get_or_create(id=1)
            return obj
        except Exception:
            class Dummy:
                auto_approve_reviews = True
                auto_verify_logged_in = True
            return Dummy()
