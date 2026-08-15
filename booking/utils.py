import os
from datetime import date
from io import BytesIO

from django.conf import settings
from PIL import Image as PILImage

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
            # Agar pixel dark/black hai (RGB < 60), to use fully transparent bana do
            if item[0] < 60 and item[1] < 60 and item[2] < 60:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)

        out_buffer = BytesIO()
        img.save(out_buffer, format="PNG")
        out_buffer.seek(0)
        return out_buffer
    except Exception as e:
        return image_path


def generate_receipt_pdf(booking):
    """
    Ghidora Transport receipt PDF generator.
    Covers ~70-75% of A4 page with professional styling & automatic signature transparency.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20,
        bottomMargin=20,
        leftMargin=20,
        rightMargin=20,
    )

    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "normal_center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9, leading=12,
    )
    label_style = ParagraphStyle(
        "label_style", parent=styles["Normal"], textColor=colors.white,
        fontName="Helvetica-Bold", fontSize=10, alignment=TA_CENTER, leading=13,
    )
    value_style = ParagraphStyle(
        "value_style", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12,
    )
    small_grey = ParagraphStyle(
        "small_grey", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8,
        textColor=colors.grey, leading=10,
    )
    company_name_style = ParagraphStyle(
        "company_name_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=22, leading=26,
        textColor=colors.HexColor("#0F2A5C"),
    )
    company_name_style_left = ParagraphStyle(
        "company_name_style_left", parent=styles["Normal"], alignment=TA_LEFT,
        fontName="Helvetica-Bold", fontSize=22, leading=26,
        textColor=colors.HexColor("#0F2A5C"),
    )
    address_style = ParagraphStyle(
        "address_style", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9,
        leading=14, textColor=colors.HexColor("#181819"),
    )
    receipt_title_style = ParagraphStyle(
        "receipt_title_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=15, leading=18,
        textColor=colors.HexColor("#065AF6"),
    )
    meta_style_label = ParagraphStyle(
        "meta_label", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12
    )
    meta_style_value = ParagraphStyle(
        "meta_value", parent=styles["Normal"], fontSize=9, leading=12
    )
    fare_label_style = ParagraphStyle(
        "fare_label_style", parent=styles["Normal"], alignment=TA_LEFT, fontSize=9,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#065F46"), leading=12,
    )
    fare_value_style = ParagraphStyle(
        "fare_value_style", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=9,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#065F46"), leading=12,
    )
    total_label_style = ParagraphStyle(
        "total_label_style", parent=styles["Normal"], alignment=TA_LEFT, fontSize=11,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#047857"), leading=14,
    )
    total_value_style = ParagraphStyle(
        "total_value_style", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=13,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#047857"), leading=16,
    )
    sig_style_left = ParagraphStyle(
        "sig_left", parent=styles["Normal"], alignment=TA_LEFT, fontSize=8, leading=11
    )
    sig_style_center = ParagraphStyle(
        "sig_center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8, leading=11
    )
    sig_style_right = ParagraphStyle(
        "sig_right", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=8, leading=11
    )
    footer_style = ParagraphStyle(
        "footer_style", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8, leading=12
    )

    elements = []

    # 1. Mantra Image Header
    mantra_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "mantra.png")
    if os.path.exists(mantra_path):
        mantra_img = _fit_image(mantra_path, max_width=4.5 * inch, max_height=0.8 * inch)
        mantra_img.hAlign = "CENTER"
        elements.append(mantra_img)
        elements.append(Spacer(1, 6))

    # 2. Logo & Company Title Side-by-Side Header
    logo_candidates = ["logo6.png", "logo3.png", "logo.png", "logo5.jpeg", "pikupwala.png"]
    found_logo_path = None
    for cand in logo_candidates:
        cand_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", cand)
        if os.path.exists(cand_path):
            found_logo_path = cand_path
            break

    if found_logo_path:
        logo = _fit_image(found_logo_path, max_width=0.85 * inch, max_height=0.65 * inch)
        title_para = Paragraph("GHIDORA TRANSPORT", company_name_style_left)
        header_table = Table(
            [[logo, title_para]],
            colWidths=[65, 270]
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]))
        header_table.hAlign = "CENTER"
        elements.append(header_table)
    else:
        elements.append(Paragraph("GHIDORA TRANSPORT", company_name_style))

    elements.append(Spacer(1, 4))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "Kodebod, Kurud, Dhamtari, Chhattisgarh &nbsp;|&nbsp; "
        "+91 7489297841 &nbsp;|&nbsp; +91 6266014139", address_style,
    ))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<hr width='100%' color='#1565C0' thickness='1.8'/>", normal))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("TRANSPORT BOOKING RECEIPT", receipt_title_style))
    elements.append(Spacer(1, 8))

    # 4. Receipt Metadata Table
    receipt_no = f"GT-{date.today().year}-{str(booking.booking_id).zfill(6)}"
    today_str = date.today().strftime("%d %B %Y")

    meta_table = Table(
        [
            [Paragraph("Receipt No.", meta_style_label), Paragraph(receipt_no, meta_style_value),
             Paragraph("Issue Date", meta_style_label), Paragraph(today_str, meta_style_value)],
            [Paragraph("Booking ID", meta_style_label), Paragraph(str(booking.booking_id), meta_style_value),
             Paragraph("Journey Date", meta_style_label), Paragraph(str(booking.journey_date), meta_style_value)],
        ],
        colWidths=[90, 160, 90, 160],
    )
    meta_table.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, -1), (-1, -1), 0.75, colors.HexColor("#D1D5DB")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # 5. Customer & Booking Details Table
    rows_data = [
        ("Customer Name", booking.name),
        ("Mobile", booking.phone),
        ("Pickup Location", booking.pickup),
        ("Destination", booking.destination),
        ("Vehicle", booking.vehicle_type),
        ("Trip Type", booking.trip_type),
        ("Distance", f"{booking.distance} KM"),
    ]
    table_rows = [[Paragraph(l, label_style), Paragraph(str(v), value_style)] for l, v in rows_data]
    details_table = Table(table_rows, colWidths=[180, 320])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1565C0")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F3F4F6")),
        ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 10))

    # 6. Fare Breakdown (Always shows Distance, Toll, Parking & Extra Charges)
    toll = float(getattr(booking, 'toll_charges', 0) or 0)
    parking = float(getattr(booking, 'parking_charges', 0) or 0)
    extra = float(getattr(booking, 'extra_charges', 0) or getattr(booking, 'other_charges', 0) or 0)
    fare_val = float(booking.fare or 0)
    total_val = float(getattr(booking, 'total_fare', None) or (fare_val + toll + parking + extra))

    fare_rows = [
        [Paragraph("Distance Fare", fare_label_style),
         Paragraph(f"Rs. {fare_val:.2f}", fare_value_style)],
        [Paragraph("Toll Charges", fare_label_style),
         Paragraph(f"Rs. {toll:.2f}", fare_value_style)],
        [Paragraph("Parking Charges", fare_label_style),
         Paragraph(f"Rs. {parking:.2f}", fare_value_style)],
        [Paragraph("Extra Charges", fare_label_style),
         Paragraph(f"Rs. {extra:.2f}", fare_value_style)],
        [Paragraph("TOTAL FARE", total_label_style),
         Paragraph(f"Rs. {total_val:.2f}", total_value_style)],
    ]

    fare_table = Table(fare_rows, colWidths=[320, 180])
    fare_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -2), colors.HexColor("#ECFDF5")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D1FAE5")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#10B981")),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#A7F3D0")),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, colors.HexColor("#10B981")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(fare_table)
    elements.append(Spacer(1, 10))

    # 7. Booking & Payment Status Bar
    status_colors = {
        "Pending": colors.HexColor("#F59E0B"),
        "Confirmed": colors.HexColor("#10B981"),
        "Completed": colors.HexColor("#3B82F6"),
        "Cancelled": colors.HexColor("#EF4444"),
    }
    status_bg = status_colors.get(booking.status, colors.HexColor("#F59E0B"))

    pay_status_text = "PENDING / UNPAID"
    pay_bg = colors.HexColor("#F59E0B")

    current_pay_status = getattr(booking, 'payment_status', 'Pending')
    if current_pay_status == 'Paid':
        pay_status_text = "VERIFIED / PAID (CASH / ONLINE)"
        pay_bg = colors.HexColor("#10B981")
    elif current_pay_status == 'Partial':
        pay_status_text = "PARTIALLY PAID"
        pay_bg = colors.HexColor("#3B82F6")
    elif current_pay_status == 'Failed':
        pay_status_text = "FAILED / REJECTED"
        pay_bg = colors.HexColor("#EF4444")
    else:
        latest_pay = None
        if hasattr(booking, 'payment_requests') and booking.payment_requests.exists():
            latest_pay = booking.payment_requests.order_by('-created_at').first()
        elif hasattr(booking, 'payments') and booking.payments.exists():
            latest_pay = booking.payments.order_by('-created_at').first()

        if latest_pay:
            st = str(latest_pay.status).upper()
            method_str = f" ({latest_pay.payment_method})" if getattr(latest_pay, 'payment_method', None) else ""
            if st in ['VERIFIED', 'COMPLETED', 'SUCCESS', 'PAID']:
                pay_status_text = f"VERIFIED / PAID{method_str}"
                pay_bg = colors.HexColor("#10B981")
            elif st in ['REJECTED', 'FAILED']:
                pay_status_text = f"FAILED{method_str}"
                pay_bg = colors.HexColor("#EF4444")
            else:
                pay_status_text = f"PENDING{method_str}"
                pay_bg = colors.HexColor("#F59E0B")
        elif booking.status in ['Completed', 'Confirmed']:
            pay_status_text = "CONFIRMED / PAID"
            pay_bg = colors.HexColor("#10B981")

    status_table_data = [
        [Paragraph("BOOKING STATUS", label_style),
         Paragraph(f"<font color='white'><b>{booking.status.upper()}</b></font>", normal)],
        [Paragraph("PAYMENT STATUS", label_style),
         Paragraph(f"<font color='white'><b>{pay_status_text}</b></font>", normal)],
    ]

    status_table = Table(status_table_data, colWidths=[250, 250])
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#374151")),
        ("BACKGROUND", (1, 0), (1, 0), status_bg),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#1F2937")),
        ("BACKGROUND", (1, 1), (1, 1), pay_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FFFFFF")),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 10))

    # 8. Coupon & Contact Footer
    footer_table = Table(
        [[
            Paragraph("<b>THANK YOU!</b><br/>Thank you for choosing<br/>Ghidora Transport", footer_style),
            Paragraph(
                "<b>DISCOUNT COUPON</b><br/>"
                "<font color='#0F2A5C' size='11'><b>GHIDORA10</b></font><br/>"
                "Get 10% off next booking", footer_style,
            ),
            Paragraph("<b>CONTACT US</b><br/> +91 7489297841<br/>+91 6266014139<br/>We're here to help", footer_style),
        ]],
        colWidths=[166, 168, 166],
    )
    footer_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 12))

    # 9. STAMP & SIGNATURE SLOTS (Stamp Left | Driver Middle | Owner Right)
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
        stamp_img = _fit_image(stamp_path, max_width=0.9 * inch, max_height=0.8 * inch)
        stamp_img.hAlign = "LEFT"
        stamp_cell_elements.append(stamp_img)
        stamp_cell_elements.append(Spacer(1, 3))
    stamp_cell_elements.append(Paragraph("<b>Official Stamp</b>", sig_style_left))

    # Driver (Middle Column) — pankaj kumar sahu
    driver_name = "pankaj kumar sahu"
    if hasattr(booking, 'assigned_driver') and booking.assigned_driver:
        driver_name = booking.assigned_driver.name

    driver_cell_elements = []
    if os.path.exists(driver_sig_path):
        driver_sign = _fit_image(driver_sig_path, max_width=0.8 * inch, max_height=0.8 * inch)
        driver_sign.hAlign = "CENTER"
        driver_cell_elements.append(driver_sign)
        driver_cell_elements.append(Spacer(1, 3))
    driver_cell_elements.append(Paragraph(
        f"<b>Driver Signature</b><br/>"
        f"{driver_name}<br/>"
        f"Driver (Assigned) - Ghidora Transport", sig_style_center,
    ))

    # Owner (Right Column) — tarun kumar sahu (Auto Black Background Removal)
    owner_cell_elements = []
    active_owner_sig = owner_sig_path if os.path.exists(owner_sig_path) else driver_sig_path
    if os.path.exists(active_owner_sig):
        # Convert black background to transparent
        cleaned_owner_sig = _remove_black_background(active_owner_sig)
        owner_sign = _fit_image(cleaned_owner_sig, max_width=0.8 * inch, max_height=0.8 * inch)
        owner_sign.hAlign = "RIGHT"
        owner_cell_elements.append(owner_sign)
        owner_cell_elements.append(Spacer(1, 3))
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
        ("LEFTPADDING", (0, 0), (0, 0), 18),
        ("RIGHTPADDING", (2, 0), (2, 0), 18),
    ]))
    elements.append(sig_row_table)
    elements.append(Spacer(1, 10))

    # 10. Footer Banner
    banner = Table(
        [[Paragraph(
            "<font color='white' size='10'><i>Thank you for choosing Ghidora Transport!</i></font>", normal,
        )]],
        colWidths=[500],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F2A5C")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 5))

    elements.append(Paragraph(
        "This is a computer generated receipt. No signature is required.", small_grey,
    ))

    doc.build(elements)

    buffer.seek(0)
    return buffer