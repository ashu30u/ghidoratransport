from django.db import models
import random


class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    DISTANCE_SOURCE_CHOICES = [
        ('Google Generated', 'Google Generated'),
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

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    pickup = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    distance = models.FloatField()

    # Distance kis tarah aayi -- Google (automatic) se ya customer ne
    # khud manually daali. Admin ke liye useful info hai.
    distance_source = models.CharField(
        max_length=20,
        choices=DISTANCE_SOURCE_CHOICES,
        default='Manual Entered'
    )

    fare = models.FloatField()

    # Toll aur parking charges alag-alag jagah alag hote hain, isliye
    # ye automatic calculate nahi hote -- admin manually daalta hai
    # booking confirm/complete karte waqt.
    toll_charges = models.FloatField(default=0, blank=True, null=True)
    parking_charges = models.FloatField(default=0, blank=True, null=True)

    # Agar toll ka SMS/payment screenshot ho, admin usko yahan upload
    # kar sakta hai proof ke taur par.
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
    # NEW FEATURE
    trip_type = models.CharField(
        max_length=20,
        default='One Way'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
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
        """
        Fare + toll + parking milaa kar final total. Template me
        {{ booking.total_fare }} likh ke seedha use kar sakte ho.
        """
        toll = self.toll_charges or 0
        parking = self.parking_charges or 0
        return self.fare + toll + parking

    def __str__(self):
        return (
            self.booking_id
            if self.booking_id
            else self.name
        )


class Review(models.Model):

    RATING_CHOICES = [
        (1, "⭐"),
        (2, "⭐⭐"),
        (3, "⭐⭐⭐"),
        (4, "⭐⭐⭐⭐"),
        (5, "⭐⭐⭐⭐⭐"),
    ]

    booking = models.OneToOneField(
    Booking,
    on_delete=models.CASCADE
)

    rating = models.IntegerField(
        choices=RATING_CHOICES
    )

    review = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.booking.name} - {self.rating}⭐"


# ============================================================
# EMAIL RECEIPT FLOW -- signals
# ============================================================
# Email booking submit hote hi NAHI jaati. Email sirf tab jaati hai
# jab admin panel se (ya kahin se bhi) Booking ka status "Completed"
# me change karke save kiya jaye, AUR pehle wo "Completed" nahi tha.
# Isse duplicate email jaane se bhi bacha jaata hai.

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


@receiver(pre_save, sender=Booking)
def _track_previous_status(sender, instance, **kwargs):
    """
    Booking save hone se PEHLE, database me jo purana status tha
    usse instance ke upar temporarily store kar leta hai, taaki
    post_save signal me hum purane aur naye status ko compare
    kar sakein.
    """
    if instance.pk:
        try:
            instance._previous_status = Booking.objects.get(pk=instance.pk).status
        except Booking.DoesNotExist:
            instance._previous_status = None
    else:
        # Naya booking hai, abhi database me hai hi nahi
        instance._previous_status = None


@receiver(post_save, sender=Booking)
def _send_email_on_completion(sender, instance, created, **kwargs):
    """
    Booking save hone ke BAAD chalta hai. Agar:
      1. Ye naya booking nahi hai (created == False, matlab update hua hai)
      2. Naya status 'Completed' hai
      3. Purana status 'Completed' nahi tha (matlab abhi-abhi change hua)
    to hi email bheji jaati hai. Agar customer ne email diya hi nahi
    (blank hai), to email chup chaap skip ho jaati hai.
    """

    previous_status = getattr(instance, '_previous_status', None)

    if not created and instance.status == 'Completed' and previous_status != 'Completed':

        if instance.email:
            from .utils import generate_receipt_pdf
            from django.core.mail import EmailMessage
            from django.conf import settings

            try:
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
                print(f"✅ Email sent to {instance.email}")

            except Exception as e:
                # Email fail ho jaye to bhi booking save process rukna nahi chahiye
                print("❌ Email send failed:", e)