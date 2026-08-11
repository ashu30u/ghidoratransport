"""
Ghidora Transport — Payment Management Models
================================================
Manual payment verification system, built so that future online
gateways (Razorpay, PhonePe, Google Pay, Cashfree, Stripe) can be
plugged in later WITHOUT changing this schema — only a small
integration layer / webhook view will be needed. See `GATEWAY_CHOICES`
and the `gateway_*` fields on PaymentRequest below.
"""
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Choice sets
# ---------------------------------------------------------------------------

class PaymentType(models.TextChoices):
    FULL = "full", "Full Payment"
    ADVANCE = "advance", "Advance Payment"
    REMAINING = "remaining", "Remaining Payment"
    CUSTOM = "custom", "Custom Amount"


class PaymentMethod(models.TextChoices):
    QR = "qr", "QR Code"
    UPI = "upi", "UPI ID"
    BANK = "bank", "Bank Transfer"


class GatewayChoice(models.TextChoices):
    """Future-ready: manual today, pluggable gateways later."""
    MANUAL = "manual", "Manual Verification"
    RAZORPAY = "razorpay", "Razorpay"
    PHONEPE = "phonepe", "PhonePe Gateway"
    GPAY = "gpay", "Google Pay Gateway"
    CASHFREE = "cashfree", "Cashfree"
    STRIPE = "stripe", "Stripe"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUBMITTED = "submitted", "Payment Submitted"
    WAITING_VERIFICATION = "waiting_verification", "Waiting Verification"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"
    REFUNDED = "refunded", "Refunded"
    COMPLETED = "completed", "Completed"

    @classmethod
    def color_map(cls):
        return {
            cls.PENDING: "#f0ad4e",              # amber
            cls.SUBMITTED: "#5bc0de",            # cyan
            cls.WAITING_VERIFICATION: "#8e6fee", # violet
            cls.VERIFIED: "#2ecc71",             # green
            cls.REJECTED: "#e74c3c",             # red
            cls.FAILED: "#c0392b",               # dark red
            cls.EXPIRED: "#7f8c8d",              # grey
            cls.REFUNDED: "#3498db",             # blue
            cls.COMPLETED: "#16a085",            # teal
        }


class RejectionReason(models.TextChoices):
    WRONG_SCREENSHOT = "wrong_screenshot", "Wrong Screenshot"
    AMOUNT_MISMATCH = "amount_mismatch", "Amount Mismatch"
    FAKE_SCREENSHOT = "fake_screenshot", "Fake Screenshot"
    BLUR_IMAGE = "blur_image", "Blur / Unreadable Image"
    DUPLICATE_TRANSACTION = "duplicate_transaction", "Duplicate Transaction"
    OTHER = "other", "Other"


class NotificationType(models.TextChoices):
    BOOKING_APPROVED = "booking_approved", "Booking Approved"
    PAYMENT_PENDING = "payment_pending", "Payment Pending"
    PAYMENT_SUBMITTED = "payment_submitted", "Payment Submitted"
    PAYMENT_VERIFIED = "payment_verified", "Payment Verified"
    PAYMENT_REJECTED = "payment_rejected", "Payment Rejected"
    RECEIPT_READY = "receipt_ready", "Receipt Ready"
    DRIVER_ASSIGNED = "driver_assigned", "Driver Assigned"
    TRIP_STARTED = "trip_started", "Trip Started"
    TRIP_COMPLETED = "trip_completed", "Trip Completed"
    PAYMENT_REMINDER = "payment_reminder", "Payment Reminder"
    BOOKING_EXPIRED = "booking_expired", "Booking Expired"


def _gen_code(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def payment_proof_upload_path(instance, filename):
    return f"payment_proofs/{instance.payment_request.booking.booking_id}/{uuid.uuid4().hex}_{filename}"


def qr_upload_path(instance, filename):
    return f"payment_settings/qr/{filename}"


# ---------------------------------------------------------------------------
# Company-wide, admin-editable payment configuration (singleton pattern)
# ---------------------------------------------------------------------------

class PaymentSettings(models.Model):
    """Admin-editable company payment configuration. Use PaymentSettings.get_solo()."""

    company_name = models.CharField(max_length=150, default="Ghidora Transport")

    # QR
    qr_code_image = models.ImageField(upload_to=qr_upload_path, blank=True, null=True)

    # UPI
    upi_id = models.CharField(max_length=100, blank=True, help_text="e.g. ghidoratransport@upi")

    # Bank transfer
    bank_name = models.CharField(max_length=150, blank=True)
    bank_branch = models.CharField(max_length=150, blank=True)
    account_holder_name = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)

    # Business rules
    default_advance_percentage = models.PositiveSmallIntegerField(
        default=30, help_text="Default % of fare requested as advance."
    )
    payment_deadline_hours = models.PositiveSmallIntegerField(
        default=24, help_text="Hours before an unpaid request expires."
    )
    reminder_hours = models.CharField(
        max_length=50, default="6,12",
        help_text="Comma separated hours (before deadline expiry) to send reminders."
    )
    payment_instructions = models.TextField(
        blank=True,
        default="Please complete the payment using any of the methods below and "
                 "upload proof of payment for verification.",
    )

    # Future gateway credentials (blank until enabled — schema stays stable)
    razorpay_key_id = models.CharField(max_length=150, blank=True)
    razorpay_key_secret = models.CharField(max_length=150, blank=True)
    stripe_publishable_key = models.CharField(max_length=150, blank=True)
    stripe_secret_key = models.CharField(max_length=150, blank=True)
    cashfree_app_id = models.CharField(max_length=150, blank=True)
    cashfree_secret_key = models.CharField(max_length=150, blank=True)
    active_gateway = models.CharField(
        max_length=20, choices=GatewayChoice.choices, default=GatewayChoice.MANUAL
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Settings"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return f"Payment Settings ({self.company_name})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def reminder_hour_list(self):
        return [int(h.strip()) for h in self.reminder_hours.split(",") if h.strip().isdigit()]


# ---------------------------------------------------------------------------
# PaymentRequest — generated by admin once a booking is approved
# ---------------------------------------------------------------------------

class PaymentRequest(models.Model):
    payment_id = models.CharField(max_length=30, unique=True, editable=False)
    booking = models.ForeignKey(
        "booking.Booking", on_delete=models.CASCADE, related_name="payment_requests"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="created_payment_requests",
    )

    payment_type = models.CharField(max_length=15, choices=PaymentType.choices, default=PaymentType.ADVANCE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    amount_already_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=25, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    due_date = models.DateTimeField()

    preferred_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices, blank=True,
        help_text="Method the customer ultimately chose (set on proof submission)."
    )

    # --- Future gateway integration fields (unused in manual flow today) ---
    gateway = models.CharField(max_length=20, choices=GatewayChoice.choices, default=GatewayChoice.MANUAL)
    gateway_order_id = models.CharField(max_length=150, blank=True)
    gateway_payment_id = models.CharField(max_length=150, blank=True)
    gateway_signature = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = _gen_code("PAY")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id} — {self.booking.booking_id} — ₹{self.amount} ({self.get_status_display()})"

    @property
    def remaining_amount(self):
        return max(self.total_fare - self.amount_already_paid - self.amount, 0)

    @property
    def is_expired(self):
        return self.status == PaymentStatus.PENDING and timezone.now() > self.due_date

    @property
    def status_color(self):
        return PaymentStatus.color_map().get(self.status, "#999999")

    @property
    def latest_proof(self):
        return self.proofs.order_by("-uploaded_at").first()


# ---------------------------------------------------------------------------
# PaymentProof — customer-submitted screenshot + transaction details
# ---------------------------------------------------------------------------

class PaymentProof(models.Model):
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, related_name="proofs")
    method_used = models.CharField(max_length=10, choices=PaymentMethod.choices)

    screenshot = models.FileField(
        upload_to=payment_proof_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "pdf"])],
    )
    file_size_bytes = models.PositiveIntegerField(default=0)

    transaction_id = models.CharField(max_length=100)
    payment_date = models.DateField()
    payment_time = models.TimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=150, blank=True)
    upi_app_used = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    reference_number = models.CharField(max_length=100, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]
        constraints = [
            # Prevent the exact same transaction ID from being used twice
            # across the whole system (duplicate transaction protection).
            models.UniqueConstraint(fields=["transaction_id"], name="unique_transaction_id"),
        ]

    def __str__(self):
        return f"Proof for {self.payment_request.payment_id} — TXN {self.transaction_id}"


# ---------------------------------------------------------------------------
# Verification decision made by admin on a given proof
# ---------------------------------------------------------------------------

class PaymentVerification(models.Model):
    class Action(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REUPLOAD_REQUESTED = "reupload_requested", "Re-upload Requested"

    proof = models.OneToOneField(PaymentProof, on_delete=models.CASCADE, related_name="verification")
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=25, choices=Action.choices)
    rejection_reason = models.CharField(max_length=30, choices=RejectionReason.choices, blank=True)
    notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    verifier_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_action_display()} — {self.proof.payment_request.payment_id}"


# ---------------------------------------------------------------------------
# Immutable audit trail of every status change on a PaymentRequest
# ---------------------------------------------------------------------------

class PaymentStatusHistory(models.Model):
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=25, choices=PaymentStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "Payment status histories"

    def __str__(self):
        return f"{self.payment_request.payment_id} -> {self.status}"


# ---------------------------------------------------------------------------
# Receipt — generated once a PaymentRequest is verified/completed
# ---------------------------------------------------------------------------

def receipt_upload_path(instance, filename):
    return f"receipts/{instance.payment_request.booking.booking_id}/{filename}"


class Receipt(models.Model):
    receipt_id = models.CharField(max_length=30, unique=True, editable=False)
    payment_request = models.OneToOneField(PaymentRequest, on_delete=models.CASCADE, related_name="receipt")
    pdf_file = models.FileField(upload_to=receipt_upload_path, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_id:
            self.receipt_id = _gen_code("RCPT")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_id


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class Notification(models.Model):
    # No customer login/account exists on Booking, so notifications are tied
    # to the booking itself rather than a User. `user` is kept (nullable) only
    # for staff-targeted notifications later; customer-facing ones leave it
    # blank and use `booking` instead.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="payment_notifications", null=True, blank=True,
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    booking = models.ForeignKey("booking.Booking", on_delete=models.CASCADE, null=True, blank=True)
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} -> {self.booking or self.user}"


# ---------------------------------------------------------------------------
# Audit log — security requirement (timestamp + IP for sensitive actions)
# ---------------------------------------------------------------------------

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action} — {self.actor}"
