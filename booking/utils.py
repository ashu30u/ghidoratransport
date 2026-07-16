import os
from datetime import date
from io import BytesIO

from django.conf import settings

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


def _fit_image(path, max_width, max_height):
    img = Image(path)
    ratio = min(
        max_width / float(img.imageWidth),
        max_height / float(img.imageHeight),
    )
    img.drawWidth = img.imageWidth * ratio
    img.drawHeight = img.imageHeight * ratio
    return img


def generate_receipt_pdf(booking):
    """
    Ghidora Transport ki receipt PDF banata hai aur BytesIO buffer return karta hai.
    Poori receipt EK page me fit ho, isliye spacing/image sizes compact rakhi gayi hain.
    Ye function 2 jagah use hoga:
      - Download Receipt button (views.py -> download_receipt)
      - Email attachment (views.py -> home)
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=10,
        bottomMargin=5,
        leftMargin=5,
        rightMargin=5,
    )

    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "normal_center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9,
    )
    label_style = ParagraphStyle(
        "label_style", parent=styles["Normal"], textColor=colors.white,
        fontName="Helvetica-Bold", fontSize=9,
    )
    value_style = ParagraphStyle(
        "value_style", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9,
    )
    small_grey = ParagraphStyle(
        "small_grey", parent=styles["Normal"], alignment=TA_CENTER, fontSize=7,
        textColor=colors.grey,
    )
    company_name_style = ParagraphStyle(
        "company_name_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=20, leading=24,
        textColor=colors.HexColor("#0F2A5C"),
    )
    address_style = ParagraphStyle(
        "address_style", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9,
        leading=12, textColor=colors.HexColor("#181819"),
    )
    receipt_title_style = ParagraphStyle(
        "receipt_title_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=14, leading=17,
        textColor=colors.HexColor("#065AF6"),
    )
    meta_style_label = ParagraphStyle(
        "meta_label", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8
    )
    meta_style_value = ParagraphStyle(
        "meta_value", parent=styles["Normal"], fontSize=8
    )
    fare_label_style = ParagraphStyle(
        "fare_label_style", parent=styles["Normal"], alignment=TA_LEFT, fontSize=9,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#065F46"),
    )
    fare_value_style = ParagraphStyle(
        "fare_value_style", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=9,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#065F46"),
    )
    total_label_style = ParagraphStyle(
        "total_label_style", parent=styles["Normal"], alignment=TA_LEFT, fontSize=11,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#047857"),
    )
    total_value_style = ParagraphStyle(
        "total_value_style", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=13,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#047857"),
    )
    sig_style_right = ParagraphStyle(
        "sig_right", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=8
    )
    stamp_caption_style = ParagraphStyle(
        "stamp_caption_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontSize=7, textColor=colors.HexColor("#374151"),
    )
    footer_style = ParagraphStyle(
        "footer_style", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8
    )
    screenshot_caption_style = ParagraphStyle(
        "screenshot_caption_style", parent=styles["Normal"], alignment=TA_CENTER,
        fontSize=8, fontName="Helvetica-Bold", textColor=colors.HexColor("#374151"),
    )

    elements = []

    mantra_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "mantra.png")
    if os.path.exists(mantra_path):
        mantra_img = _fit_image(mantra_path, max_width=4.0 * inch, max_height=0.7 * inch)
        mantra_img.hAlign = "CENTER"
        elements.append(mantra_img)
        elements.append(Spacer(0, 4))

    logo_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "logo.png")
    if os.path.exists(logo_path):
        logo = _fit_image(logo_path, max_width=1.6 * inch, max_height=0.9 * inch)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 4))

    elements.append(Paragraph("GHIDORA TRANSPORT", company_name_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph(
        "Kodebod, Kurud, Dhamtari, Chhattisgarh &nbsp;|&nbsp; "
        "+91 7489297841 &nbsp;|&nbsp; +91 6266014139", address_style,
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<hr width='100%' color='#1565C0' thickness='1.5'/>", normal))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("TRANSPORT BOOKING RECEIPT", receipt_title_style))
    elements.append(Spacer(1, 5))

    receipt_no = f"GT-{date.today().year}-{str(booking.booking_id).zfill(6)}"
    today_str = date.today().strftime("%d %B %Y")

    meta_table = Table(
        [
            [Paragraph("Receipt No.", meta_style_label), Paragraph(receipt_no, meta_style_value),
             Paragraph("Issue Date", meta_style_label), Paragraph(today_str, meta_style_value)],
            [Paragraph("Booking ID", meta_style_label), Paragraph(str(booking.booking_id), meta_style_value),
             Paragraph("Journey Date", meta_style_label), Paragraph(str(booking.journey_date), meta_style_value)],
        ],
        colWidths=[80, 160, 80, 160],
    )
    meta_table.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 5))

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
    details_table = Table(table_rows, colWidths=[180, 300])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1565C0")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F3F4F6")),
        ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 6))

    # ================================
    # FARE BREAKDOWN (Distance + Toll + Parking = Total)
    # ================================
    toll = booking.toll_charges or 0
    parking = booking.parking_charges or 0
    total = booking.total_fare

    fare_rows = [
        [Paragraph("Distance Fare", fare_label_style),
         Paragraph(f"Rs. {booking.fare:.2f}", fare_value_style)],
    ]

    if toll > 0:
        fare_rows.append([
            Paragraph("Toll Charges", fare_label_style),
            Paragraph(f"Rs. {toll:.2f}", fare_value_style),
        ])

    if parking > 0:
        fare_rows.append([
            Paragraph("Parking Charges", fare_label_style),
            Paragraph(f"Rs. {parking:.2f}", fare_value_style),
        ])

    fare_rows.append([
        Paragraph("TOTAL FARE", total_label_style),
        Paragraph(f"Rs. {total:.2f}", total_value_style),
    ])

    fare_table = Table(fare_rows, colWidths=[300, 180])
    fare_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -2), colors.HexColor("#ECFDF5")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D1FAE5")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#10B981")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#10B981")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(fare_table)
    elements.append(Spacer(1, 6))

    status_colors = {
        "Pending": colors.HexColor("#F59E0B"),
        "Confirmed": colors.HexColor("#10B981"),
        "Completed": colors.HexColor("#3B82F6"),
        "Cancelled": colors.HexColor("#EF4444"),
    }
    status_bg = status_colors.get(booking.status, colors.HexColor("#F59E0B"))
    status_table = Table(
        [[Paragraph("BOOKING STATUS", label_style),
          Paragraph(f"<font color='white'><b>{booking.status.upper()}</b></font>", normal)]],
        colWidths=[240, 240],
    )
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#374151")),
        ("BACKGROUND", (1, 0), (1, 0), status_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 6))

   

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
        colWidths=[160, 160, 160],
    )
    footer_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 6))

    signature_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "signature.png")
    stamp_path = os.path.join(settings.BASE_DIR, "booking", "static", "images", "stamp.png")

    blank_cell = Paragraph("", sig_style_right)

    stamp_cell_elements = []
    if os.path.exists(stamp_path):
        stamp_img = _fit_image(stamp_path, max_width=1.0 * inch, max_height=0.9 * inch)
        stamp_img.hAlign = "LEFT"
        stamp_cell_elements.append(stamp_img)
        stamp_cell_elements.append(Spacer(1, 0))
        stamp_cell_elements.append(Paragraph("<b> Official Company Stamp</b>", stamp_caption_style))
    else:
        stamp_cell_elements.append(Paragraph("", stamp_caption_style))

    sign_cell_elements = []
    if os.path.exists(signature_path):
        sign = _fit_image(signature_path, max_width=0.8 * inch, max_height=1.0 * inch)
        sign.hAlign = "RIGHT"
        sign_cell_elements.append(sign)
    sign_cell_elements.append(Paragraph(
        "<b>Authorized Signature</b><br/>"
        "pankaj kumar Sahu<br/>"
        "Owner - Ghidora Transport", sig_style_right,
    ))

    sig_row_table = Table(
        [[blank_cell, stamp_cell_elements, sign_cell_elements]],
        colWidths=[190, 130, 160],
    )
    sig_row_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
    ]))
    elements.append(sig_row_table)
    elements.append(Spacer(1, 4))

    banner = Table(
        [[Paragraph(
            "<font color='white' size='10'><i>Thank you for choosing Ghidora Transport!</i></font>", normal,
        )]],
        colWidths=[480],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F2A5C")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 4))

    elements.append(Paragraph(
        "This is a computer generated receipt. No signature is required.", small_grey,
    ))

    doc.build(elements)

    buffer.seek(0)
    return buffer