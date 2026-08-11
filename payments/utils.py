"""
Utility helpers for the payments app: PDF receipts, QR codes, IP lookup,
notification dispatch, and duplicate-upload hashing.
"""
import os
import hashlib
import io
import urllib.parse
from datetime import date
from PIL import Image as PILImage

from django.conf import settings
from django.core.files.base import ContentFile

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Image,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

from .models import Notification, PaymentSettings


# ---------------------------------------------------------------------------
# Client IP (for audit logging)
# ---------------------------------------------------------------------------

def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ---------------------------------------------------------------------------
# Duplicate-file protection
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
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        booking=booking,
        payment_request=payment_request,
    )


# ---------------------------------------------------------------------------
# QR & UPI Link Generation
# ---------------------------------------------------------------------------

def build_upi_link(upi_id, payee_name, amount=None, note=""):
    params = {
        "pa": upi_id,
        "pn": payee_name,
    }
    if amount:
        params["am"] = f"{float(amount):.2f}"
    if note:
        params["tn"] = note
    return "upi://pay?" + urllib.parse.urlencode(params)


def generate_upi_qr(upi_id, payee_name, amount=None, note=""):
    import qrcode
    upi_url = build_upi_link(upi_id, payee_name, amount, note)
    img = qrcode.make(upi_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name="upi_qr.png")


# ---------------------------------------------------------------------------
# Image Helpers (Fit Image & Remove Black Background for Owner Signature)
# ---------------------------------------------------------------------------

def _fit_image(path_or_stream, max_width, max_height):
    img = Image(path_or_stream)
    ratio = min(
        max_width / float(img.imageWidth),
        max_height / float(img.imageHeight),
    )
    img.drawWidth = img.imageWidth * ratio
    img.drawHeight = img.imageHeight * ratio
    return img


def _remove_black_background(image_path):
    """
    Signature image me se black background ko transparent me convert karta hai.
    """
    try:
        img = PILImage.open(image_path).convert("RGBA")
        datas = img.getdata()

        new_data = []
        for item in datas:
            if item[0] < 60 and item[1] < 60 and item[2] < 60:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)

        out_buffer = io.BytesIO()
        img.save(out_buffer, format="PNG")
        out_buffer.seek(0)
        return out_buffer
    except Exception as e:
        return image_path


# ---------------------------------------------------------------------------
# SINGLE-PAGE PERFECT COMPACT PDF RECEIPT GENERATOR
# ---------------------------------------------------------------------------

def generate_receipt_pdf(payment_request):
    """
    Builds a compact single-page A4 PDF receipt.
    Includes Mantra, Logo, Company Details, Metadata, Booking/Customer Info,
    Full Payment Breakdown, Status, 1-Line Offer Strip, Stamp & Signatures.
    """
    booking = payment_request.booking
    proof = payment_request.latest_proof
    receipt = getattr(payment_request, 'receipt', None)
    receipt_id = receipt.receipt_id if receipt else f"RCPT-{payment_request.payment_id}"

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=10,
        bottomMargin=10,
        leftMargin=18,
        rightMargin=18,
    )

    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "normal_center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8.5, leading=11,
    )
    label_style = ParagraphStyle(
        "label_style", parent=styles["Normal"], textColor=colors.white,
        fontName="Helvetica-Bold", fontSize=8.5, alignment=TA_CENTER, leading=11,
    )
    value_style = ParagraphStyle(
        "value_style", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11,
    )
    small_grey = ParagraphStyle(
        "small_grey", parent=styles["Normal"], alignment=TA_CENTER, fontSize=7.5,
        textColor=colors.grey, leading=9,
    )
    company_name_style = ParagraphStyle(
        "company_name_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=20, leading=22,
        textColor=colors.HexColor("#0F2A5C"),
    )
    address_style = ParagraphStyle(
        "address_style", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8,
        leading=11, textColor=colors.HexColor("#181819"),
    )
    receipt_title_style = ParagraphStyle(
        "receipt_title_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=13, leading=15,
        textColor=colors.HexColor("#065AF6"),
    )
    meta_style_label = ParagraphStyle(
        "meta_label", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10
    )
    meta_style_value = ParagraphStyle(
        "meta_value", parent=styles["Normal"], fontSize=8, leading=10
    )
    section_heading = ParagraphStyle(
        "section_heading", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.HexColor("#0F2A5C"), spaceBefore=2, spaceAfter=2
    )
    fare_label_style = ParagraphStyle(
        "fare_label_style", parent=styles["Normal"], alignment=TA_LEFT, fontSize=8,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#065F46"), leading=10,
    )
    fare_value_style = ParagraphStyle(
        "fare_value_style", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=8,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#065F46"), leading=10,
    )
    total_label_style = ParagraphStyle(
        "total_label_style", parent=styles["Normal"], alignment=TA_LEFT, fontSize=9.5,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#047857"), leading=12,
    )
    total_value_style = ParagraphStyle(
        "total_value_style", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=10.5,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#047857"), leading=13,
    )
    offer_strip_style = ParagraphStyle(
        "offer_strip", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8,
        textColor=colors.HexColor("#0F2A5C"), leading=10
    )
    sig_style_left = ParagraphStyle(
        "sig_left", parent=styles["Normal"], alignment=TA_LEFT, fontSize=7.5, leading=9
    )
    sig_style_center = ParagraphStyle(
        "sig_center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=7.5, leading=9
    )
    sig_style_right = ParagraphStyle(
        "sig_right", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=7.5, leading=9
    )

    elements = []

    # 1. Mantra Image Header
    mantra_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "mantra.png")
    if os.path.exists(mantra_path):
        mantra_img = _fit_image(mantra_path, max_width=4.0 * inch, max_height=0.55 * inch)
        mantra_img.hAlign = "CENTER"
        elements.append(mantra_img)
        elements.append(Spacer(1, 2))

    # 2. Logo Image Header
    logo_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "logo.png")
    if os.path.exists(logo_path):
        logo = _fit_image(logo_path, max_width=1.4 * inch, max_height=0.75 * inch)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 2))

    # 3. Company Title & Address
    elements.append(Paragraph("GHIDORA TRANSPORT", company_name_style))
    elements.append(Paragraph(
        "Kodebod, Kurud, Dhamtari, Chhattisgarh &nbsp;|&nbsp; "
        "+91 7489297841 &nbsp;|&nbsp; +91 6266014139", address_style,
    ))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("<hr width='100%' color='#1565C0' thickness='1.2'/>", normal))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph("TRANSPORT PAYMENT RECEIPT", receipt_title_style))
    elements.append(Spacer(1, 3))

    # 4. Receipt Metadata Table
    today_str = date.today().strftime("%d %B %Y")

    meta_table = Table(
        [
            [Paragraph("Receipt No.", meta_style_label), Paragraph(receipt_id, meta_style_value),
             Paragraph("Issue Date", meta_style_label), Paragraph(today_str, meta_style_value)],
            [Paragraph("Booking ID", meta_style_label), Paragraph(str(booking.booking_id), meta_style_value),
             Paragraph("Journey Date", meta_style_label), Paragraph(str(booking.journey_date or "-"), meta_style_value)],
        ],
        colWidths=[85, 165, 85, 165],
    )
    meta_table.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 3))

    # 5. Booking & Customer Details Table
    elements.append(Paragraph("Booking & Customer Details", section_heading))
    b_cargo = getattr(booking, 'cargo_type', '-') or '-'
    b_trip = getattr(booking, 'trip_type', '-') or '-'
    b_veh = getattr(booking, 'vehicle_type', '-') or '-'
    b_dist = f"{booking.distance} KM" if getattr(booking, 'distance', None) else '-'

    rows_data = [
        ("Customer Name", booking.name or "-"),
        ("Mobile Number", booking.phone or "-"),
        ("Pickup Location", booking.pickup or "-"),
        ("Destination", booking.destination or "-"),
        ("Vehicle Type", b_veh),
        ("Trip Type", b_trip),
        ("Distance", b_dist),
    ]
    table_rows = [[Paragraph(l, label_style), Paragraph(str(v), value_style)] for l, v in rows_data]
    details_table = Table(table_rows, colWidths=[160, 340])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1565C0")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 3))

    # 6. Payment Details Table (Full Detailed Breakdown)
    elements.append(Paragraph("Payment Details", section_heading))
    txn_id_val = proof.transaction_id if (proof and proof.transaction_id) else "-"
    method_val = proof.get_method_used_display() if proof else "UPI ID"
    pay_date_val = proof.payment_date.strftime("%d %b %Y") if (proof and proof.payment_date) else today_str

    amt_paid_this_req = float(payment_request.amount or 0)
    amt_paid_so_far = float(payment_request.amount_already_paid or 0)
    rem_balance = float(payment_request.remaining_amount or 0)

    pay_data = [
        ("Payment ID", payment_request.payment_id),
        ("Payment Type", payment_request.get_payment_type_display()),
        ("Total Fare", f"Rs. {payment_request.total_fare:.2f}"),
        ("Amount Paid (this request)", f"Rs. {amt_paid_this_req:.2f}"),
        ("Total Amount Paid So Far", f"Rs. {amt_paid_so_far:.2f}"),
        ("Remaining Balance", f"Rs. {rem_balance:.2f}"),
        ("Payment Status", payment_request.get_status_display()),
        ("Transaction ID", txn_id_val),
        ("Method Used", method_val),
        ("Payment Date", pay_date_val),
    ]
    pay_rows = [[Paragraph(l, label_style), Paragraph(str(v), value_style)] for l, v in pay_data]
    pay_table = Table(pay_rows, colWidths=[160, 340])
    pay_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0D47A1")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F1F5F9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(pay_table)
    elements.append(Spacer(1, 3))

    # 7. Fare Breakdown & Big Total Box
    toll = float(getattr(booking, 'toll_charges', 0) or 0)
    parking = float(getattr(booking, 'parking_charges', 0) or 0)
    extra = float(getattr(booking, 'extra_charges', 0) or getattr(booking, 'other_charges', 0) or 0)
    fare_val = float(booking.fare or 0)
    total_val = float(getattr(booking, 'total_fare', None) or (fare_val + toll + parking + extra))

    fare_rows = [
        [Paragraph("Distance Fare", fare_label_style), Paragraph(f"Rs. {fare_val:.2f}", fare_value_style)],
        [Paragraph("Toll / Parking / Extra Charges", fare_label_style), Paragraph(f"Rs. {(toll + parking + extra):.2f}", fare_value_style)],
        [Paragraph("TOTAL BOOKING FARE", total_label_style), Paragraph(f"Rs. {total_val:.2f}", total_value_style)],
    ]
    fare_table = Table(fare_rows, colWidths=[330, 170])
    fare_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -2), colors.HexColor("#ECFDF5")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D1FAE5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#A7F3D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(fare_table)
    elements.append(Spacer(1, 3))

    # 8. Booking & Payment Status Bar
    status_table_data = [
        [Paragraph("BOOKING STATUS", label_style),
         Paragraph(f"<font color='white'><b>{booking.status.upper()}</b></font>", normal)],
        [Paragraph("PAYMENT STATUS", label_style),
         Paragraph(f"<font color='white'><b>{payment_request.get_status_display().upper()}</b></font>", normal)],
    ]
    status_table = Table(status_table_data, colWidths=[250, 250])
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#374151")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#10B981")),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#1F2937")),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#059669")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FFFFFF")),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 3))

    # 🌟 9. Simple One-Line Offer & Contact Strip (No brackets, no extra boxes)
    offer_text = "<b>Coupon: GHIDORA10</b> (10% Off Next Booking) &nbsp;|&nbsp; <b>Thank You For Choosing Ghidora Transport</b> &nbsp;|&nbsp; <b>Support:</b> +91 7489297841"
    offer_table = Table([[Paragraph(offer_text, offer_strip_style)]], colWidths=[500])
    offer_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    elements.append(offer_table)
    elements.append(Spacer(1, 4))

    # 10. STAMP & SIGNATURE SLOTS (Stamp Left | Driver Middle | Owner Right)
    stamp_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "stamp.png")
    driver_sig_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "signature.png")
    owner_sig_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "ownersighn4.jpeg")
    
    if not os.path.exists(owner_sig_path):
        for ext in ['.jpg', '.png', '.jpeg']:
            alt_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", f"ownersighn{ext}")
            if os.path.exists(alt_path):
                owner_sig_path = alt_path
                break

    # Stamp (Left Column)
    stamp_cell_elements = []
    if os.path.exists(stamp_path):
        stamp_img = _fit_image(stamp_path, max_width=0.75 * inch, max_height=0.65 * inch)
        stamp_img.hAlign = "LEFT"
        stamp_cell_elements.append(stamp_img)
        stamp_cell_elements.append(Spacer(1, 1))
    stamp_cell_elements.append(Paragraph("<b>Official Stamp</b>", sig_style_left))

    # Driver (Middle Column) — pankaj kumar sahu
    driver_name = "pankaj kumar sahu"
    if hasattr(booking, 'assigned_driver') and booking.assigned_driver:
        driver_name = booking.assigned_driver.name

    driver_cell_elements = []
    if os.path.exists(driver_sig_path):
        driver_sign = _fit_image(driver_sig_path, max_width=0.65 * inch, max_height=0.65 * inch)
        driver_sign.hAlign = "CENTER"
        driver_cell_elements.append(driver_sign)
        driver_cell_elements.append(Spacer(1, 1))
    driver_cell_elements.append(Paragraph(
        f"<b>Driver Signature</b><br/>"
        f"{driver_name}<br/>"
        f"Driver (Assigned)", sig_style_center,
    ))

    # Owner (Right Column) — tarun kumar sahu (Auto Black Background Removal)
    owner_cell_elements = []
    active_owner_sig = owner_sig_path if os.path.exists(owner_sig_path) else driver_sig_path
    if os.path.exists(active_owner_sig):
        cleaned_owner_sig = _remove_black_background(active_owner_sig)
        owner_sign = _fit_image(cleaned_owner_sig, max_width=0.65 * inch, max_height=0.65 * inch)
        owner_sign.hAlign = "RIGHT"
        owner_cell_elements.append(owner_sign)
        owner_cell_elements.append(Spacer(1, 1))
    owner_cell_elements.append(Paragraph(
        "<b>Owner Signature</b><br/>"
        "tarun kumar sahu<br/>"
        "Owner - Ghidora Transport", sig_style_right,
    ))

    sig_row_table = Table(
        [[stamp_cell_elements, driver_cell_elements, owner_cell_elements]],
        colWidths=[166, 168, 166],
    )
    sig_row_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
    ]))
    elements.append(sig_row_table)
    elements.append(Spacer(1, 3))

    # 11. Footer Banner
    banner = Table(
        [[Paragraph(
            "<font color='white' size='8'><i>Thank you for choosing Ghidora Transport! Safe & Reliable Logistics</i></font>", normal,
        )]],
        colWidths=[500],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F2A5C")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 2))

    elements.append(Paragraph(
        "This is a computer generated receipt. No signature is required.", small_grey,
    ))

    doc.build(elements)
    buffer.seek(0)
    filename = f"Receipt_{booking.booking_id}_{payment_request.payment_id}.pdf"
    return ContentFile(buffer.getvalue(), name=filename)


def _kv_table(rows):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    table = Table(rows, colWidths=[160, 340])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4a5568")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
    ]))
    return table