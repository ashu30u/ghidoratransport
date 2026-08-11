from django.contrib import admin

from .models import (
    PaymentSettings, PaymentRequest, PaymentProof, PaymentVerification,
    PaymentStatusHistory, Receipt, Notification, AuditLog,
)


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ("company_name", "upi_id", "default_advance_percentage",
                     "payment_deadline_hours", "active_gateway", "updated_at")

    def has_add_permission(self, request):
        # Singleton — only one settings row should ever exist.
        return not PaymentSettings.objects.exists()


class PaymentProofInline(admin.TabularInline):
    model = PaymentProof
    extra = 0
    readonly_fields = ("uploaded_at", "uploaded_ip")


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "booking", "payment_type", "amount",
                     "status", "due_date", "created_at")
    list_filter = ("status", "payment_type", "gateway")
    search_fields = ("payment_id", "booking__booking_id", "booking__name", "booking__phone")
    inlines = [PaymentProofInline]
    readonly_fields = ("payment_id", "created_at", "updated_at")


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("payment_request", "method_used", "transaction_id",
                     "amount_paid", "payment_date", "uploaded_at")
    list_filter = ("method_used",)
    search_fields = ("transaction_id", "payment_request__payment_id")
    readonly_fields = ("uploaded_at", "uploaded_ip", "file_size_bytes")


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(admin.ModelAdmin):
    list_display = ("proof", "action", "rejection_reason", "verified_by", "verified_at")
    list_filter = ("action", "rejection_reason")
    readonly_fields = ("verified_at", "verifier_ip")


@admin.register(PaymentStatusHistory)
class PaymentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("payment_request", "status", "changed_by", "changed_at")
    list_filter = ("status",)
    readonly_fields = ("changed_at",)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_id", "payment_request", "generated_at")
    readonly_fields = ("receipt_id", "generated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "ip_address", "timestamp")
    list_filter = ("action",)
    readonly_fields = ("timestamp",)
    search_fields = ("action", "actor__username", "details")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
