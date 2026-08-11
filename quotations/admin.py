from django.contrib import admin
from .models import Quotation


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'name', 'phone', 'vehicle_type', 'final_amount', 'status', 'is_approved', 'created_at')
    list_filter = ('status', 'quote_type', 'is_approved')
    search_fields = ('quote_number', 'name', 'phone')
