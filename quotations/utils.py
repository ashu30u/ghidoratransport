from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_quotation_pdf(quotation):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFillColor(colors.HexColor('#2979ff'))
    c.rect(0, height - 30 * mm, width, 30 * mm, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 15 * mm, "GHIDORA TRANSPORT")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 22 * mm, "OFFICIAL QUOTATION")

    y = height - 45 * mm
    c.setFillColor(colors.black)

    def row(label, value, y):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(25 * mm, y, f"{label}:")
        c.setFont("Helvetica", 11)
        c.drawString(70 * mm, y, str(value))
        return y - 9 * mm

    y = row("Quote No", quotation.quote_number, y)
    y = row("Customer", quotation.name, y)
    y = row("Phone", quotation.phone, y)
    y = row("Route", f"{quotation.pickup} -> {quotation.destination}", y)
    if quotation.goods_type:
        y = row("Goods", quotation.goods_type, y)
    y = row("Vehicle", quotation.vehicle_type, y)
    y = row("Distance", f"{quotation.distance} KM", y)
    y = row("Estimated Time", f"{quotation.estimated_time_hours} Hours", y)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor('#2979ff'))
    c.drawString(25 * mm, y, f"Amount: Rs. {quotation.final_amount}")
    c.setFillColor(colors.black)
    y -= 12 * mm

    y = row("Valid Till", quotation.valid_till.strftime("%d %b %Y, %I:%M %p"), y)

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 15 * mm, "This is a computer generated quotation - Ghidora Transport")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
