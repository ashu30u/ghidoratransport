"""
expenses/models.py

Expense tracking ke 4 alag hisse:
1. FuelExpense    - har trip ka diesel kharch
2. TollParkingExpense - toll/parking/other kharch (manual entry)
3. MaintenanceRecord  - vehicle ki servicing/repair history
4. DriverPayment      - driver ko per-trip ya monthly payment
"""

from django.db import models

from booking.models import Booking
from drivers.models import Driver, Vehicle


class FuelExpense(models.Model):
    """Har booking/trip ka diesel kharch."""

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='fuel_expenses'
    )
    liters = models.FloatField(help_text="Kitne liter diesel bhara")
    rate_per_liter = models.FloatField(help_text="Us din ka diesel rate per liter")
    date = models.DateField(auto_now_add=True)
    notes = models.CharField(max_length=200, blank=True, null=True)

    @property
    def total_cost(self):
        """Liters x Rate - automatically calculate hota hai."""
        return round(self.liters * self.rate_per_liter, 2)

    def __str__(self):
        return f"{self.booking.booking_id} - Fuel ₹{self.total_cost}"


class TollParkingExpense(models.Model):
    """Har booking ka toll/parking/other kharch - admin manually daalta hai."""

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='toll_expenses'
    )
    toll = models.FloatField(default=0)
    parking = models.FloatField(default=0)
    other = models.FloatField(default=0)
    other_note = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    @property
    def total_cost(self):
        return round(self.toll + self.parking + self.other, 2)

    def __str__(self):
        return f"{self.booking.booking_id} - Toll/Parking ₹{self.total_cost}"


class MaintenanceRecord(models.Model):
    """Vehicle ki servicing/repair history."""

    MAINTENANCE_TYPE_CHOICES = [
        ('Engine Oil Change', 'Engine Oil Change'),
        ('Tyre Replacement', 'Tyre Replacement'),
        ('Brake Service', 'Brake Service'),
        ('General Service', 'General Service'),
        ('Repair', 'Repair'),
        ('Other', 'Other'),
    ]

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='maintenance_records'
    )
    maintenance_type = models.CharField(
        max_length=30, choices=MAINTENANCE_TYPE_CHOICES, default='General Service'
    )
    date = models.DateField()
    cost = models.FloatField()
    notes = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.maintenance_type} ₹{self.cost}"


class DriverPayment(models.Model):
    """Driver ko payment - per-trip ya monthly salary dono support karta hai."""

    PAYMENT_TYPE_CHOICES = [
        ('Per Trip', 'Per Trip'),
        ('Monthly Salary', 'Monthly Salary'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name='payments'
    )
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES, default='Per Trip'
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='driver_payments',
        help_text="Sirf 'Per Trip' payment ke liye - kaunsi booking ke liye ye payment hai"
    )
    month = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Sirf 'Monthly Salary' ke liye - jaise 'July 2026'"
    )
    amount = models.FloatField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver.name} - {self.payment_type} ₹{self.amount} ({self.status})"