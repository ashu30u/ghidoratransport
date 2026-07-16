"""
expenses/utils.py

Trip Profit Calculation - sabse important part.

Formula:
    Profit = Booking Fare - (Fuel + Toll/Parking + Driver Payment)

Ye function ek booking leta hai aur uska poora income/expense/profit
breakdown ek dictionary me return karta hai.
"""

from .models import FuelExpense, TollParkingExpense, DriverPayment


def calculate_trip_profit(booking):
    """
    Ek booking ke liye income, expense breakdown, aur final profit
    calculate karta hai.
    """
    income = booking.total_fare  # Booking model me already fare+toll+parking wala property hai

    fuel_total = sum(f.total_cost for f in FuelExpense.objects.filter(booking=booking))
    toll_parking_total = sum(t.total_cost for t in TollParkingExpense.objects.filter(booking=booking))
    driver_payment_total = sum(
        d.amount for d in DriverPayment.objects.filter(booking=booking, payment_type='Per Trip')
    )

    total_expense = fuel_total + toll_parking_total + driver_payment_total
    profit = income - total_expense

    return {
        "booking_id": booking.booking_id,
        "income": round(income, 2),
        "fuel_expense": round(fuel_total, 2),
        "toll_parking_expense": round(toll_parking_total, 2),
        "driver_payment_expense": round(driver_payment_total, 2),
        "total_expense": round(total_expense, 2),
        "profit": round(profit, 2),
    }


def calculate_all_profits(bookings):
    """Multiple bookings ke liye ek saath profit list nikalta hai (report ke liye)."""
    return [calculate_trip_profit(b) for b in bookings]