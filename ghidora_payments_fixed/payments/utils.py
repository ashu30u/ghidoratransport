"""Utility helpers for the payments app: PDF receipts, QR codes, IP lookup,
notification dispatch, and duplicate-upload hashing.
"""
import hashlib
import io

from django.core.files.base import ContentFile

from .models import Notification


# ---------------------------------------------------------------------------
# Client IP (for audit logging)
# ---------------------------------------------------------------------------

def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ---------------------------------------------------------------------------
# Duplicate-file protection: hash uploaded proof content
# ---------------------------------------------------------------------------

def file_sha256(django_file):
    django_file.seek(0)
    digest = hashlib.sha256()
    for chunk in django_file.chunks():
        digest.update(chunk)
    django_file.seek(0)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def notify(notification_type, message, booking=None, payment_request=None, user=None):
    """Create a notification tied to a booking. `user` is optional — customers
    have no login account, so customer-facing notifications leave it blank
    and are matched to a person via `booking` instead.
    """
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        booking=booking,
        payment_request=payment_request,
    )


# ---------------------------------------------------------------------------
# UPI deep link (upi://pay?...) — tapping this on a phone opens the user's
# installed UPI app (GPay/PhonePe/Paytm/etc.) directly with the payee,
# amount, and note pre-filled. Used both for QR generation and for a
# tap-to-pay button/link on the customer payment page.
# ---------------------------------------------------------------------------

def build_upi_link(upi_id, payee_name, amount=None, note=""):
    upi_url = f"upi://pay?pa={upi_id}&pn={payee_name.replace(' ', '%20')}"
    if amount:
        upi_url += f"&am={amount}"
    if note:
        upi_url += f"&tn={note.replace(' ', '%20')}"
    return upi_url


# ---------------------------------------------------------------------------
# QR code generation (used if admin wants to auto-generate a UPI QR
# instead of uploading one manually). Requires the `qrcode` package.
# ---------------------------------------------------------------------------

def generate_upi_qr(upi_id, payee_name, amount=None, note=""):
    """Returns a Django ContentFile (PNG) encoding a standard UPI deep link."""
    import qrcode

    upi_url = build_upi_link(upi_id, payee_name, amount, note)

    img = qrcode.make(upi_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name="upi_qr.png")


# ---------------------------------------------------------------------------
# PDF Receipt generator (uses reportlab — no external services required)
# ---------------------------------------------------------------------------

def generate_receipt_pdf(payment_request):
    """Builds a professional PDF receipt for a PaymentRequest and returns
    a Django ContentFile ready to be saved onto Receipt.pdf_file.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from django.utils import timezone

    from .models import PaymentSettings

    settings_obj = PaymentSettings.get_solo()
    booking = payment_request.booking
    receipt = payment_request.receipt

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleBrand", parent=styles["Title"], fontSize=20,
        textColor=colors.HexColor("#0d1b3e"), spaceAfter=2,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#4a5568"),
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading3"], fontSize=12,
        textColor=colors.HexColor("#1a3fa0"), spaceBefore=14, spaceAfter=6,
    )

    elements = []

    # Header
    header_data = [[
        Paragraph(f"<b>{settings_obj.company_name}</b>", title_style),
        Paragraph(f"Receipt #: <b>{receipt.receipt_id}</b><br/>"
                  f"Date: {timezone.now():%d %b %Y, %I:%M %p}", sub_style),
    ]]
    header_table = Table(header_data, colWidths=[300, 180])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        "Manual Payment Verification Receipt", sub_style
    ))
    elements.append(Spacer(1, 6 * mm))

    # Booking details
    elements.append(Paragraph("Booking Details", section_style))
    booking_rows = [
        ["Booking ID", booking.booking_id],
        ["Pickup Location", booking.pickup],
        ["Destination", booking.destination],
        ["Cargo", booking.cargo_type or "-"],
        ["Trip Type", booking.trip_type or "-"],
        ["Vehicle", booking.vehicle_type or "-"],
        ["Distance", f"{booking.distance} km" if booking.distance else "-"],
    ]
    elements.append(_kv_table(booking_rows))

    # Customer details (no login account — Booking stores these directly)
    elements.append(Paragraph("Customer Details", section_style))
    customer_rows = [
        ["Name", booking.name or "-"],
        ["Phone", booking.phone or "-"],
        ["Email", booking.email or "-"],
    ]
    elements.append(_kv_table(customer_rows))

    # Payment details
    elements.append(Paragraph("Payment Details", section_style))
    proof = payment_request.latest_proof
    payment_rows = [
        ["Payment ID", payment_request.payment_id],
        ["Payment Type", payment_request.get_payment_type_display()],
        ["Total Fare", f"Rs. {payment_request.total_fare}"],
        ["Amount Paid (this request)", f"Rs. {payment_request.amount}"],
        ["Remaining Balance", f"Rs. {payment_request.remaining_amount}"],
        ["Status", payment_request.get_status_display()],
    ]
    if proof:
        payment_rows += [
            ["Transaction ID", proof.transaction_id],
            ["Method Used", proof.get_method_used_display()],
            ["Payment Date", proof.payment_date.strftime("%d %b %Y")],
        ]
    elements.append(_kv_table(payment_rows))

    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(
        "This is a system-generated receipt for a manually verified "
        "payment. For any discrepancy, contact support with your "
        "Payment ID and Booking ID.", sub_style,
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        f"<b>{settings_obj.company_name}</b> — Thank you for choosing us for "
        f"your transport needs.", sub_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    filename = f"receipt_{receipt.receipt_id}.pdf"
    return ContentFile(buffer.getvalue(), name=filename)


def _kv_table(rows):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    table = Table(rows, colWidths=[180, 300])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4a5568")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
    ]))
    return table