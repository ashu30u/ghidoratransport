from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    PaymentSettings, PaymentRequest, PaymentProof, PaymentVerification,
    PaymentStatusHistory, Receipt, Notification, AuditLog, PaymentStatus,
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


# ---------------------------------------------------------------------------
# Bulk Admin Actions
# ---------------------------------------------------------------------------

@admin.action(description="✅ Mark ALL DONE & Email PDF Receipt to Customer(s)")
def mark_all_done_bulk_proof(modeladmin, request, queryset):
    from .utils import mark_payment_all_done_and_send_receipt
    count = 0
    emailed = 0
    for proof in queryset:
        res = mark_payment_all_done_and_send_receipt(
            proof.payment_request, proof=proof,
            verified_by=request.user, request=request
        )
        count += 1
        if res.get("email_sent"):
            emailed += 1
    modeladmin.message_user(
        request,
        f"🎉 {count} payment(s) marked ALL DONE! Official PDF receipts emailed to {emailed} customer(s)."
    )


@admin.action(description="✅ Mark ALL DONE & Email PDF Receipt to Customer(s)")
def mark_all_done_bulk_request(modeladmin, request, queryset):
    from .utils import mark_payment_all_done_and_send_receipt
    count = 0
    emailed = 0
    for pr in queryset:
        res = mark_payment_all_done_and_send_receipt(
            pr, verified_by=request.user, request=request
        )
        count += 1
        if res.get("email_sent"):
            emailed += 1
    modeladmin.message_user(
        request,
        f"🎉 {count} payment request(s) marked ALL DONE! Official PDF receipts emailed to {emailed} customer(s)."
    )


# ---------------------------------------------------------------------------
# PaymentRequestAdmin
# ---------------------------------------------------------------------------

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "booking", "customer_email_display", "payment_type", "amount",
                     "status", "all_done_button", "due_date", "created_at")
    list_filter = ("status", "payment_type", "gateway")
    search_fields = ("payment_id", "booking__booking_id", "booking__name", "booking__phone", "booking__email")
    inlines = [PaymentProofInline]
    readonly_fields = ("payment_id", "created_at", "updated_at", "all_done_action_card")
    actions = [mark_all_done_bulk_request]

    fieldsets = (
        ("🌟 Quick Action: All Done & Send Receipt", {
            "fields": ("all_done_action_card",),
            "description": "Click the button below to verify payment, generate the official PDF receipt, and email it directly to the customer in 1-click."
        }),
        ("📌 Request Details", {
            "fields": ("payment_id", "booking", "created_by", "payment_type", "amount", "total_fare", "amount_already_paid", "status", "due_date")
        }),
        ("Gateway & Details", {
            "fields": ("preferred_method", "gateway", "gateway_order_id", "gateway_payment_id"),
            "classes": ("collapse",)
        }),
        ("Audit Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def customer_email_display(self, obj):
        email = obj.booking.email or (obj.booking.user.email if obj.booking.user else "")
        return email or mark_safe('<span style="color:#9ca3af;">(No email)</span>')
    customer_email_display.short_description = "Customer Email"

    def all_done_button(self, obj):
        receipt = getattr(obj, 'receipt', None)
        is_done = obj.status in [PaymentStatus.VERIFIED, PaymentStatus.COMPLETED]
        if is_done and receipt and receipt.is_sent:
            return format_html(
                '<div style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap;">'
                '<span style="background:#10B981; color:#fff; padding:4px 8px; border-radius:10px; font-weight:700; font-size:11px;">✅ ALL DONE (Receipt Emailed)</span>'
                '<a href="/payments/receipt/{}/view/" target="_blank" style="background:#0284c7; color:#fff; padding:3px 7px; border-radius:6px; font-size:11px; text-decoration:none;">📄 View</a>'
                '</div>',
                obj.payment_id
            )
        elif is_done:
            return format_html(
                '<div style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap;">'
                '<span style="background:#059669; color:#fff; padding:4px 8px; border-radius:10px; font-weight:700; font-size:11px;">✅ ALL DONE</span>'
                '<a href="/payments/admin-panel/all-done/{}/" style="background:#7c3aed; color:#fff; padding:3px 7px; border-radius:6px; font-size:11px; text-decoration:none;" onclick="return confirm(\'Resend receipt email to customer now?\');">✉️ Resend Receipt</a>'
                '</div>',
                obj.payment_id
            )
        else:
            return format_html(
                '<a href="/payments/admin-panel/all-done/{}/" class="button" '
                'style="background:linear-gradient(135deg, #10B981, #059669) !important; color:#ffffff !important; padding:5px 12px !important; border-radius:8px !important; font-weight:800 !important; font-size:11px !important; text-decoration:none !important; box-shadow: 0 2px 6px rgba(16,185,129,0.4); white-space:nowrap; display:inline-block;" '
                'onclick="return confirm(\'Mark this payment as ALL DONE and automatically send the PDF receipt to customer email?\');">'
                '🚀 Mark ALL DONE &amp; Send Receipt'
                '</a>',
                obj.payment_id
            )
    all_done_button.short_description = "All Done & Receipt"

    def all_done_action_card(self, obj):
        booking = obj.booking
        receipt = getattr(obj, 'receipt', None)
        customer_email = booking.email or (booking.user.email if booking.user else None) or "Not provided"
        is_done = obj.status in [PaymentStatus.VERIFIED, PaymentStatus.COMPLETED]
        
        if is_done:
            sent_info = f"Receipt emailed to: <b>{receipt.sent_to_email}</b> on {receipt.sent_at.strftime('%d %b %Y %H:%M')}" if (receipt and receipt.is_sent and receipt.sent_to_email) else "Receipt generated."
            return format_html(
                '<div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:12px; padding:16px; max-width:650px;">'
                '<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">'
                '<span style="background:#10B981; color:#fff; padding:4px 10px; border-radius:12px; font-weight:800; font-size:12px;">✅ PAYMENT ALL DONE &amp; VERIFIED</span>'
                '</div>'
                '<p style="margin:0 0 10px; color:#065F46; font-size:13px;">{}</p>'
                '<div style="display:flex; gap:10px;">'
                '<a href="/payments/receipt/{}/view/" target="_blank" class="button" style="background:#0284c7 !important; color:#fff !important; font-weight:700; text-decoration:none; padding:6px 14px; border-radius:6px;">👁️ View Receipt PDF</a>'
                '<a href="/payments/admin-panel/all-done/{}/" class="button" style="background:#059669 !important; color:#fff !important; font-weight:700; text-decoration:none; padding:6px 14px; border-radius:6px;" onclick="return confirm(\'Resend receipt email to customer now?\');">✉️ Resend Receipt Email</a>'
                '</div>'
                '</div>',
                sent_info, obj.payment_id, obj.payment_id
            )
        else:
            return format_html(
                '<div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:12px; padding:18px; max-width:650px;">'
                '<h4 style="margin:0 0 8px; color:#92400E; font-size:15px; font-weight:700;">🌟 1-Click Complete: Mark ALL DONE &amp; Send Receipt</h4>'
                '<p style="margin:0 0 12px; color:#78350F; font-size:13px; line-height:1.5;">'
                'Clicking the button below will immediately:<br/>'
                '1. <b>Approve</b> the payment verification.<br/>'
                '2. Mark payment request as <b>VERIFIED</b>.<br/>'
                '3. <b>Generate</b> the official stamped PDF receipt.<br/>'
                '4. <b>Email the receipt directly</b> to the customer (<b>{}</b>).'
                '</p>'
                '<a href="/payments/admin-panel/all-done/{}/" class="button" '
                'style="background:linear-gradient(135deg, #10B981, #047857) !important; color:#ffffff !important; font-weight:800 !important; font-size:13px !important; padding:10px 20px !important; border-radius:8px !important; text-decoration:none !important; display:inline-block; box-shadow:0 3px 10px rgba(16,185,129,0.35);" '
                'onclick="return confirm(\'Mark this payment as ALL DONE and automatically send official receipt PDF to {} now?\');">'
                '🚀 MARK ALL DONE &amp; EMAIL RECEIPT TO CUSTOMER'
                '</a>'
                '</div>',
                customer_email, obj.payment_id, customer_email
            )
    all_done_action_card.short_description = "All Done Quick Action"


# ---------------------------------------------------------------------------
# PaymentProofAdmin
# ---------------------------------------------------------------------------

@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("payment_request", "customer_info", "method_used", "transaction_id",
                     "amount_paid", "payment_date", "all_done_button", "uploaded_at")
    list_filter = ("method_used", "payment_request__status")
    search_fields = ("transaction_id", "payment_request__payment_id", "payment_request__booking__booking_id", "payment_request__booking__name", "payment_request__booking__phone")
    readonly_fields = ("uploaded_at", "uploaded_ip", "file_size_bytes", "all_done_action_card", "screenshot_preview")
    actions = [mark_all_done_bulk_proof]

    fieldsets = (
        ("🌟 Quick Action: All Done & Send Receipt", {
            "fields": ("all_done_action_card",),
            "description": "If payment is complete, click below to mark as ALL DONE and send the official receipt PDF to the customer in 1 click."
        }),
        ("📌 Proof Information", {
            "fields": ("payment_request", "method_used", "amount_paid", "transaction_id", "payment_date", "payment_time", "bank_name", "upi_app_used", "remarks")
        }),
        ("📷 Screenshot / Document", {
            "fields": ("screenshot_preview", "screenshot", "file_size_bytes")
        }),
        ("Audit Timestamps", {
            "fields": ("uploaded_at", "uploaded_ip"),
            "classes": ("collapse",)
        }),
    )

    def customer_info(self, obj):
        b = obj.payment_request.booking
        return f"{b.name} (#{b.booking_id})"
    customer_info.short_description = "Customer"

    def screenshot_preview(self, obj):
        if not obj.screenshot:
            return "No screenshot uploaded"
        url = obj.screenshot.url
        if url.lower().endswith('.pdf'):
            return format_html('<a href="{}" target="_blank" class="button" style="background:#0284c7; color:#fff; padding:6px 12px; border-radius:6px; text-decoration:none;">📄 View PDF Proof</a>', url)
        return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height:220px; border-radius:8px; border:1px solid #374151;" title="Click to view full screenshot"/></a>', url, url)
    screenshot_preview.short_description = "Proof Preview"

    def all_done_button(self, obj):
        pr = obj.payment_request
        receipt = getattr(pr, 'receipt', None)
        is_done = pr.status in [PaymentStatus.VERIFIED, PaymentStatus.COMPLETED]
        if is_done and receipt and receipt.is_sent:
            return format_html(
                '<div style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap;">'
                '<span style="background:#10B981; color:#fff; padding:4px 8px; border-radius:10px; font-weight:700; font-size:11px;">✅ ALL DONE (Receipt Emailed)</span>'
                '<a href="/payments/receipt/{}/view/" target="_blank" style="background:#0284c7; color:#fff; padding:3px 7px; border-radius:6px; font-size:11px; text-decoration:none;">📄 View</a>'
                '</div>',
                pr.payment_id
            )
        elif is_done:
            return format_html(
                '<div style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap;">'
                '<span style="background:#059669; color:#fff; padding:4px 8px; border-radius:10px; font-weight:700; font-size:11px;">✅ ALL DONE</span>'
                '<a href="/payments/admin-panel/all-done/{}/" style="background:#7c3aed; color:#fff; padding:3px 7px; border-radius:6px; font-size:11px; text-decoration:none;" onclick="return confirm(\'Resend receipt email to customer now?\');">✉️ Resend Receipt</a>'
                '</div>',
                pr.payment_id
            )
        else:
            return format_html(
                '<a href="/payments/admin-panel/all-done/{}/" class="button" '
                'style="background:linear-gradient(135deg, #10B981, #059669) !important; color:#ffffff !important; padding:5px 12px !important; border-radius:8px !important; font-weight:800 !important; font-size:11px !important; text-decoration:none !important; box-shadow: 0 2px 6px rgba(16,185,129,0.4); white-space:nowrap; display:inline-block;" '
                'onclick="return confirm(\'Mark this payment proof as ALL DONE and automatically send the official receipt PDF to customer email?\');">'
                '🚀 Mark ALL DONE &amp; Send Receipt'
                '</a>',
                pr.payment_id
            )
    all_done_button.short_description = "All Done & Receipt"

    def all_done_action_card(self, obj):
        pr = obj.payment_request
        booking = pr.booking
        receipt = getattr(pr, 'receipt', None)
        customer_email = booking.email or (booking.user.email if booking.user else None) or "Not provided"
        is_done = pr.status in [PaymentStatus.VERIFIED, PaymentStatus.COMPLETED]
        
        if is_done:
            sent_info = f"Receipt emailed to: <b>{receipt.sent_to_email}</b> on {receipt.sent_at.strftime('%d %b %Y %H:%M')}" if (receipt and receipt.is_sent and receipt.sent_to_email) else "Receipt generated."
            return format_html(
                '<div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:12px; padding:16px; max-width:650px;">'
                '<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">'
                '<span style="background:#10B981; color:#fff; padding:4px 10px; border-radius:12px; font-weight:800; font-size:12px;">✅ PAYMENT ALL DONE &amp; VERIFIED</span>'
                '</div>'
                '<p style="margin:0 0 10px; color:#065F46; font-size:13px;">{}</p>'
                '<div style="display:flex; gap:10px;">'
                '<a href="/payments/receipt/{}/view/" target="_blank" class="button" style="background:#0284c7 !important; color:#fff !important; font-weight:700; text-decoration:none; padding:6px 14px; border-radius:6px;">👁️ View Receipt PDF</a>'
                '<a href="/payments/admin-panel/all-done/{}/" class="button" style="background:#059669 !important; color:#fff !important; font-weight:700; text-decoration:none; padding:6px 14px; border-radius:6px;" onclick="return confirm(\'Resend receipt email to customer now?\');">✉️ Resend Receipt Email</a>'
                '</div>'
                '</div>',
                sent_info, pr.payment_id, pr.payment_id
            )
        else:
            return format_html(
                '<div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:12px; padding:18px; max-width:650px;">'
                '<h4 style="margin:0 0 8px; color:#92400E; font-size:15px; font-weight:700;">🌟 1-Click Complete: Mark ALL DONE &amp; Send Receipt</h4>'
                '<p style="margin:0 0 12px; color:#78350F; font-size:13px; line-height:1.5;">'
                'Clicking the button below will immediately:<br/>'
                '1. <b>Approve</b> this payment proof verification.<br/>'
                '2. Mark payment request as <b>VERIFIED</b>.<br/>'
                '3. <b>Generate</b> the official stamped PDF receipt.<br/>'
                '4. <b>Email the receipt directly</b> to the customer (<b>{}</b>).'
                '</p>'
                '<a href="/payments/admin-panel/all-done/{}/" class="button" '
                'style="background:linear-gradient(135deg, #10B981, #047857) !important; color:#ffffff !important; font-weight:800 !important; font-size:13px !important; padding:10px 20px !important; border-radius:8px !important; text-decoration:none !important; display:inline-block; box-shadow:0 3px 10px rgba(16,185,129,0.35);" '
                'onclick="return confirm(\'Mark this payment proof as ALL DONE and automatically send official receipt PDF to {} now?\');">'
                '🚀 MARK ALL DONE &amp; EMAIL RECEIPT TO CUSTOMER'
                '</a>'
                '</div>',
                customer_email, pr.payment_id, customer_email
            )
    all_done_action_card.short_description = "All Done Quick Action"


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
    list_display = ("receipt_id", "payment_request", "is_sent", "sent_to_email", "sent_at", "view_receipt_link", "generated_at")
    list_filter = ("is_sent", "generated_at")
    readonly_fields = ("receipt_id", "generated_at", "view_receipt_link")

    def view_receipt_link(self, obj):
        return format_html(
            '<a href="/payments/receipt/{}/view/" target="_blank" class="button" style="background:#0284c7; color:#fff; padding:4px 10px; border-radius:6px; font-size:11px; text-decoration:none;">👁️ View PDF</a>',
            obj.payment_request.payment_id
        )
    view_receipt_link.short_description = "PDF Receipt"


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
