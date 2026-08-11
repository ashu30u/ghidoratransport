import random
from django.db import models
from django.utils import timezone
from datetime import timedelta


VEHICLE_RATES = {
    'Mahindra Pickup': 20,
    'Mahindra Bolero': 30,
    'Mahindra Cruiser': 30,
    'Magic': 15,
    'Van': 22,
    'Mini Bus': 40,
    'Tata Ace': 20,
    'Mini Truck': 35,
    'Tractor Trolley': 50,
}

VEHICLE_CHOICES = [(k, k) for k in VEHICLE_RATES.keys()]

# Kitni amount se upar admin ki manual approval chahiye
ADMIN_APPROVAL_THRESHOLD = 50000


class Quotation(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    ]

    QUOTE_TYPE_CHOICES = [
        ('Instant', 'Instant Estimate'),
        ('Custom', 'Custom Quotation'),
    ]

    quote_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Customer details
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    # Trip details
    pickup = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    goods_type = models.CharField(max_length=150, blank=True)
    weight = models.CharField(max_length=50, blank=True, help_text="e.g. 500 KG")
    quantity = models.PositiveIntegerField(default=1)
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_CHOICES, default='Mahindra Pickup')
    distance = models.FloatField(default=0)

    # Pricing
    base_fare = models.FloatField(default=0)
    discount = models.FloatField(default=0, blank=True)

    # Workflow
    quote_type = models.CharField(max_length=10, choices=QUOTE_TYPE_CHOICES, default='Instant')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    is_approved = models.BooleanField(default=False, help_text="Bade amount (₹50,000+) ke liye admin approval")
    rejection_reason = models.CharField(max_length=100, blank=True)

    valid_till = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    converted_booking = models.ForeignKey(
        'booking.Booking', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='quotation'
    )

    def save(self, *args, **kwargs):
        if not self.quote_number:
            for _ in range(5):
                candidate = "QT" + str(random.randint(10000, 99999))
                if not Quotation.objects.filter(quote_number=candidate).exists():
                    self.quote_number = candidate
                    break

        if not self.valid_till:
            self.valid_till = timezone.now() + timedelta(hours=24)

        if not self.base_fare and self.distance:
            rate = VEHICLE_RATES.get(self.vehicle_type, 20)
            self.base_fare = self.distance * rate

        super().save(*args, **kwargs)

    @property
    def final_amount(self):
        return round(self.base_fare - (self.discount or 0), 2)

    @property
    def estimated_time_hours(self):
        if self.distance:
            return round(self.distance / 40, 1)  # avg 40 km/h assume
        return 0

    @property
    def needs_admin_approval(self):
        return self.final_amount >= ADMIN_APPROVAL_THRESHOLD

    @property
    def is_expired_now(self):
        return self.valid_till and timezone.now() > self.valid_till and self.status == 'Pending'

    def __str__(self):
        return self.quote_number or f"Quote-{self.pk}"
