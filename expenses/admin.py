"""
expenses/admin.py

Django admin panel me expense models register karta hai, taaki
aap http://127.0.0.1:8000/admin/ pe jaake inko easily add/edit/
delete kar sakein - bina koi code likhe.
"""

from django.contrib import admin

from .models import FuelExpense, TollParkingExpense, MaintenanceRecord, DriverPayment


@admin.register(FuelExpense)
class FuelExpenseAdmin(admin.ModelAdmin):
    list_display = ('booking', 'liters', 'rate_per_liter', 'total_cost', 'date')
    list_filter = ('date',)
    search_fields = ('booking__booking_id',)


@admin.register(TollParkingExpense)
class TollParkingExpenseAdmin(admin.ModelAdmin):
    list_display = ('booking', 'toll', 'parking', 'other', 'total_cost', 'date')
    list_filter = ('date',)
    search_fields = ('booking__booking_id',)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_type', 'cost', 'date')
    list_filter = ('maintenance_type', 'date')
    search_fields = ('vehicle__vehicle_number',)


@admin.register(DriverPayment)
class DriverPaymentAdmin(admin.ModelAdmin):
    list_display = ('driver', 'payment_type', 'amount', 'status', 'date')
    list_filter = ('payment_type', 'status', 'date')
    search_fields = ('driver__name',)