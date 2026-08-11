from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PaymentProofForm, PaymentVerificationForm, PaymentSettingsForm, PaymentRequestForm
from .models import (
    PaymentRequest, PaymentProof, PaymentVerification, PaymentSettings,
    PaymentStatus, Receipt, AuditLog,
)
from .utils import get_client_ip, generate_receipt_pdf, build_upi_link


def is_staff(user):
    return user.is_authenticated and user.is_staff


# ---------------------------------------------------------------------------
# CUSTOMER-FACING VIEWS
# ---------------------------------------------------------------------------

def customer_payment_page(request, payment_id):
    # No customer login exists — the payment_id itself is the unique,
    # unguessable token that grants access (like a payment link).
    payment_request = get_object_or_404(
        PaymentRequest.objects.select_related("booking"),
        payment_id=payment_id,
    )
    settings_obj = PaymentSettings.get_solo()

    if payment_request.is_expired and payment_request.status == PaymentStatus.PENDING:
        payment_request.status = PaymentStatus.EXPIRED
        payment_request.save(update_fields=["status"])

    form = PaymentProofForm()
    if request.method == "POST":
        if payment_request.status not in (PaymentStatus.PENDING, PaymentStatus.REJECTED):
            messages.error(request, "This payment request no longer accepts new proof uploads.")
            return redirect("payments:customer_payment_page", payment_id=payment_id)

        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.payment_request = payment_request
            proof.file_size_bytes = form.cleaned_data["screenshot"].size
            proof.uploaded_ip = get_client_ip(request)
            proof.save()

            AuditLog.objects.create(
                actor=None, action="payment_proof_uploaded",
                details=f"Payment {payment_request.payment_id}, TXN {proof.transaction_id} "
                        f"(booking {payment_request.booking.booking_id})",
                ip_address=get_client_ip(request),
            )
            messages.success(request, "Payment proof submitted. We'll verify it shortly.")
            return redirect("payments:customer_payment_page", payment_id=payment_id)
        else:
            messages.error(request, "Please correct the errors below.")

    upi_pay_link = None
    if settings_obj.upi_id:
        upi_pay_link = build_upi_link(
            settings_obj.upi_id, settings_obj.company_name,
            amount=payment_request.amount,
            note=f"{payment_request.booking.booking_id} {payment_request.payment_id}",
        )

    context = {
        "payment_request": payment_request,
        "booking": payment_request.booking,
        "settings_obj": settings_obj,
        "form": form,
        "status_color": payment_request.status_color,
        "upi_pay_link": upi_pay_link,
    }
    return render(request, "payments/customer_payment_page.html", context)


def payment_history(request, booking_id):
    requests_qs = (
        PaymentRequest.objects.filter(booking__booking_id=booking_id)
        .select_related("booking")
        .prefetch_related("proofs")
        .order_by("-created_at")
    )
    return render(request, "payments/payment_history.html", {
        "payment_requests": requests_qs, "booking_id": booking_id,
    })


def download_receipt(request, payment_id):
    payment_request = get_object_or_404(PaymentRequest, payment_id=payment_id)
    receipt = getattr(payment_request, "receipt", None)
    if not receipt or not receipt.pdf_file:
        raise Http404("Receipt not available yet.")
    return FileResponse(receipt.pdf_file.open("rb"), as_attachment=True,
                         filename=f"{receipt.receipt_id}.pdf")


# ---------------------------------------------------------------------------
# ADMIN-FACING VIEWS
# ---------------------------------------------------------------------------

@user_passes_test(is_staff)
def admin_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    base_qs = PaymentRequest.objects.all()
    stats = {
        "pending_verification": base_qs.filter(status=PaymentStatus.WAITING_VERIFICATION).count(),
        "verified": base_qs.filter(status=PaymentStatus.VERIFIED).count(),
        "rejected": base_qs.filter(status=PaymentStatus.REJECTED).count(),
        "todays_payments": base_qs.filter(created_at__date=today).count(),
        "monthly_payments": base_qs.filter(created_at__date__gte=month_start).count(),
        "total_collection": base_qs.filter(status__in=[PaymentStatus.VERIFIED, PaymentStatus.COMPLETED])
                                    .aggregate(total=Sum("amount_already_paid"))["total"] or 0,
        "advance_collection": base_qs.filter(payment_type="advance", status=PaymentStatus.VERIFIED)
                                      .aggregate(total=Sum("amount"))["total"] or 0,
        "remaining_collection": base_qs.filter(payment_type="remaining", status=PaymentStatus.VERIFIED)
                                        .aggregate(total=Sum("amount"))["total"] or 0,
    }

    daily_collection = (
        base_qs.filter(status__in=[PaymentStatus.VERIFIED, PaymentStatus.COMPLETED])
        .annotate(day=TruncDate("created_at"))
        .values("day").order_by("day").annotate(total=Sum("amount"))
    )

    pending_queue = (
        base_qs.filter(status=PaymentStatus.WAITING_VERIFICATION)
        .select_related("booking").order_by("created_at")
    )

    context = {
        "stats": stats,
        "daily_collection": list(daily_collection),
        "pending_queue": pending_queue,
    }
    return render(request, "payments/admin_dashboard.html", context)


@user_passes_test(is_staff)
def admin_create_payment_request(request, booking_id):
    from booking.models import Booking
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if request.method == "POST":
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            pr = form.save(commit=False)
            pr.booking = booking
            pr.created_by = request.user
            hours = PaymentSettings.get_solo().payment_deadline_hours
            if not pr.due_date:
                pr.due_date = timezone.now() + timezone.timedelta(hours=hours)
            pr.save()
            messages.success(request, f"Payment request {pr.payment_id} created.")
            return redirect("payments:admin_dashboard")
    else:
        settings_obj = PaymentSettings.get_solo()
        advance_default = round(float(booking.total_fare) * settings_obj.default_advance_percentage / 100, 2)
        form = PaymentRequestForm(initial={
            "total_fare": booking.total_fare,
            "amount": advance_default,
            "payment_type": "advance",
            "due_date": timezone.now() + timezone.timedelta(hours=settings_obj.payment_deadline_hours),
        })

    return render(request, "payments/admin_create_payment_request.html",
                  {"form": form, "booking": booking})


@user_passes_test(is_staff)
def admin_verification_panel(request, payment_id):
    payment_request = get_object_or_404(
        PaymentRequest.objects.select_related("booking"),
        payment_id=payment_id,
    )
    proof = payment_request.latest_proof
    if not proof:
        raise Http404("No proof submitted for this payment request yet.")

    form = PaymentVerificationForm()
    if request.method == "POST":
        form = PaymentVerificationForm(request.POST)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.proof = proof
            verification.verified_by = request.user
            verification.verifier_ip = get_client_ip(request)
            verification.save()

            AuditLog.objects.create(
                actor=request.user, action=f"payment_{verification.action}",
                details=f"Payment {payment_request.payment_id}",
                ip_address=get_client_ip(request),
            )

            # Auto-generate receipt on approval
            if verification.action == PaymentVerification.Action.APPROVED:
                payment_request.refresh_from_db()
                receipt, _ = Receipt.objects.get_or_create(payment_request=payment_request)
                pdf_file = generate_receipt_pdf(payment_request)
                receipt.pdf_file.save(pdf_file.name, pdf_file, save=True)

            messages.success(request, "Verification decision saved.")
            return redirect("payments:admin_dashboard")

    return render(request, "payments/admin_verification_panel.html", {
        "payment_request": payment_request, "proof": proof, "form": form,
    })


@user_passes_test(is_staff)
def admin_payment_settings(request):
    settings_obj = PaymentSettings.get_solo()
    if request.method == "POST":
        form = PaymentSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment settings updated.")
            return redirect("payments:admin_payment_settings")
    else:
        form = PaymentSettingsForm(instance=settings_obj)
    return render(request, "payments/admin_payment_settings.html", {"form": form})