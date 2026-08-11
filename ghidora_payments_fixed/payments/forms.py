from django import forms
from django.core.exceptions import ValidationError

from .models import (
    PaymentProof, PaymentRequest, PaymentVerification, PaymentSettings,
    PaymentMethod, RejectionReason,
)

MAX_UPLOAD_SIZE_MB = 10


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = [
            "method_used", "screenshot", "transaction_id", "reference_number",
            "payment_date", "payment_time", "amount_paid", "bank_name",
            "upi_app_used", "remarks",
        ]
        widgets = {
            "method_used": forms.Select(attrs={"class": "form-select glass-input"}),
            "screenshot": forms.FileInput(attrs={
                "class": "form-control glass-input",
                "accept": ".png,.jpg,.jpeg,.pdf",
            }),
            "transaction_id": forms.TextInput(attrs={"class": "form-control glass-input"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control glass-input"}),
            "payment_date": forms.DateInput(attrs={"class": "form-control glass-input", "type": "date"}),
            "payment_time": forms.TimeInput(attrs={"class": "form-control glass-input", "type": "time"}),
            "amount_paid": forms.NumberInput(attrs={"class": "form-control glass-input", "step": "0.01"}),
            "bank_name": forms.TextInput(attrs={"class": "form-control glass-input"}),
            "upi_app_used": forms.TextInput(attrs={"class": "form-control glass-input"}),
            "remarks": forms.Textarea(attrs={"class": "form-control glass-input", "rows": 3}),
        }

    def clean_screenshot(self):
        f = self.cleaned_data["screenshot"]
        if f.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB.")
        allowed = ("png", "jpg", "jpeg", "pdf")
        ext = f.name.rsplit(".", 1)[-1].lower()
        if ext not in allowed:
            raise ValidationError("Unsupported file type. Allowed: PNG, JPG, JPEG, PDF.")
        return f

    def clean_transaction_id(self):
        txn_id = self.cleaned_data["transaction_id"].strip()
        qs = PaymentProof.objects.filter(transaction_id=txn_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(
                "This Transaction ID has already been submitted. "
                "Duplicate transactions are not allowed."
            )
        return txn_id


class PaymentRequestForm(forms.ModelForm):
    """Used by admin to generate a payment request for an approved booking."""

    class Meta:
        model = PaymentRequest
        fields = ["payment_type", "amount", "total_fare", "amount_already_paid", "due_date"]
        widgets = {
            "payment_type": forms.Select(attrs={"class": "form-select glass-input"}),
            "amount": forms.NumberInput(attrs={"class": "form-control glass-input", "step": "0.01"}),
            "total_fare": forms.NumberInput(attrs={"class": "form-control glass-input", "step": "0.01"}),
            "amount_already_paid": forms.NumberInput(attrs={"class": "form-control glass-input", "step": "0.01"}),
            "due_date": forms.DateTimeInput(attrs={"class": "form-control glass-input", "type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        amount = cleaned.get("amount")
        total_fare = cleaned.get("total_fare")
        already_paid = cleaned.get("amount_already_paid") or 0
        if amount and total_fare and (already_paid + amount) > total_fare:
            raise ValidationError("Requested amount plus amount already paid exceeds the total fare.")
        return cleaned


class PaymentVerificationForm(forms.ModelForm):
    class Meta:
        model = PaymentVerification
        fields = ["action", "rejection_reason", "notes"]
        widgets = {
            "action": forms.Select(attrs={"class": "form-select glass-input"}),
            "rejection_reason": forms.Select(attrs={"class": "form-select glass-input"}),
            "notes": forms.Textarea(attrs={"class": "form-control glass-input", "rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("action") == PaymentVerification.Action.REJECTED and not cleaned.get("rejection_reason"):
            raise ValidationError("Please select a rejection reason.")
        return cleaned


class PaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = PaymentSettings
        fields = [
            "company_name", "qr_code_image", "upi_id", "bank_name", "bank_branch",
            "account_holder_name", "account_number", "ifsc_code",
            "default_advance_percentage", "payment_deadline_hours", "reminder_hours",
            "payment_instructions", "active_gateway",
        ]
        widgets = {
            field: forms.TextInput(attrs={"class": "form-control glass-input"})
            for field in [
                "company_name", "upi_id", "bank_name", "bank_branch",
                "account_holder_name", "account_number", "ifsc_code", "reminder_hours",
            ]
        }
        widgets.update({
            "qr_code_image": forms.FileInput(attrs={"class": "form-control glass-input"}),
            "default_advance_percentage": forms.NumberInput(attrs={"class": "form-control glass-input"}),
            "payment_deadline_hours": forms.NumberInput(attrs={"class": "form-control glass-input"}),
            "payment_instructions": forms.Textarea(attrs={"class": "form-control glass-input", "rows": 4}),
            "active_gateway": forms.Select(attrs={"class": "form-select glass-input"}),
        })
