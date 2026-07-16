"""
expenses/views.py

Profit Report page - saari bookings ki income/expense/profit list
dikhata hai. URL: /admin-panel/profit-report/
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from booking.models import Booking
from .utils import calculate_all_profits


@staff_member_required
def profit_report(request):
    bookings = Booking.objects.filter(status='Completed').order_by('-booking_date')
    profit_data = calculate_all_profits(bookings)

    total_income = sum(item['income'] for item in profit_data)
    total_expense = sum(item['total_expense'] for item in profit_data)
    total_profit = sum(item['profit'] for item in profit_data)

    context = {
        'profit_data': profit_data,
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'total_profit': round(total_profit, 2),
    }
    return render(request, 'expenses/profit_report.html', context)