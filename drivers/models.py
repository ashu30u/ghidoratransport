from django.db import models
from django.core.validators import RegexValidator


mobile_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Mobile number 10 digits ka hona chahiye (e.g. 9876543210)"
)


class Driver(models.Model):
    STATUS_CHOICES = (
        ('available', '🟢 Available'),
        ('busy', '🔴 Busy'),
    )

    name = models.CharField(max_length=100, verbose_name="Driver Name")
    mobile = models.CharField(max_length=10, validators=[mobile_validator], unique=True)
    photo = models.ImageField(upload_to='drivers/photos/', blank=True, null=True)
    license_number = models.CharField(max_length=30, unique=True)
    address = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Experience (Years)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    # Jab tak sirf ek hi driver hai, use "default" maan kar permanently assign karenge.
    # Admin chahe to isko kisi doosre driver par manually shift kar sakta hai.
    is_default = models.BooleanField(
        default=False,
        verbose_name="Default Driver (auto-assign)",
        help_text="Naye bookings me is driver ko automatically assign kiya jayega, jab tak admin khud koi aur driver na choose kare."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Agar system me abhi koi bhi driver nahi hai, to yehi pehla driver
        # automatically default (permanent assign) ban jayega.
        if not self.pk and not Driver.objects.exists():
            self.is_default = True

        # Ek waqt me sirf ek hi driver "default" ho sakta hai.
        if self.is_default:
            Driver.objects.exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    @property
    def vehicle(self):
        return getattr(self, 'vehicle_detail', None)


class Vehicle(models.Model):
    driver = models.OneToOneField(
        Driver, on_delete=models.CASCADE, related_name='vehicle_detail'
    )
    vehicle_number = models.CharField(max_length=20, unique=True, help_text="e.g. CG05 AB 1234")
    vehicle_type = models.CharField(max_length=100, help_text="e.g. Mahindra Pickup / Mini Truck")
    capacity = models.CharField(max_length=50, help_text="e.g. 1 Ton")
    vehicle_image = models.ImageField(upload_to='drivers/vehicles/', blank=True, null=True)
    rc_number = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.vehicle_type} - {self.vehicle_number}"


def get_assigned_driver():
    """
    Booking ke liye driver decide karne ka helper.
    - Agar koi driver 'is_default=True' hai, wahi return hoga (permanent-assign case,
      jab sirf ek hi driver system me ho).
    - Warna pehla 'available' driver return hoga.
    - Admin panel se assign_booking action ke through isko override kiya ja sakta hai.
    """
    default_driver = Driver.objects.filter(is_default=True, status='available').first()
    if default_driver:
        return default_driver
    return Driver.objects.filter(status='available').first()
