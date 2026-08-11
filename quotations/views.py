import urllib.parse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Quotation, ADMIN_APPROVAL_THRESHOLD
from .forms import QuoteRequestForm, AdminQuoteEditForm
from .utils import generate_quotation_pdf
from booking.models import Booking


def _send_quote_email(quotation):
    if not quotation.email:
        return False
    try:
        mail = EmailMessage(
            subject=f"Your Quotation {quotation.quote_number} - Ghidora Transport",
            body=(
                f"Dear {quotation.name},\n\n"
                f"Your quotation is ready.\n\n"
                f"Quote No: {quotation.quote_number}\n"
                f"Route: {quotation.pickup} -> {quotation.destination}\n"
                f"Vehicle: {quotation.vehicle_type}\n"
                f"Amount: Rs. {quotation.final_amount}\n"
                f"Valid Till: {quotation.valid_till.strftime('%d %b %Y, %I:%M %p')}\n\n"
                f"Quotation PDF attached hai.\n\nGhidora Transport"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[quotation.email],
        )
        pdf_buffer = generate_quotation_pdf(quotation)
        mail.attach(f"Quotation_{quotation.quote_number}.pdf", pdf_buffer.getvalue(), "application/pdf")
        mail.send(fail_silently=False)
        return True
    except Exception as e:
        print("❌ Quotation email failed:", e)
        return False


# ---------------------------------------------------------------------
# CUSTOMER SIDE
# ---------------------------------------------------------------------

def quote_request(request):
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.quote_type = 'Instant'
            quotation.save()
            _send_quote_email(quotation)
            return redirect('quotations:quote_detail', quote_number=quotation.quote_number)
    else:
        form = QuoteRequestForm()

    return render(request, 'quotations/quote_form.html', {'form': form})


def quote_detail(request, quote_number):
    quotation = get_object_or_404(Quotation, quote_number=quote_number)

    if quotation.is_expired_now:
        quotation.status = 'Expired'
        quotation.save(update_fields=['status'])

    wa_text = urllib.parse.quote(
        f"Hello {quotation.name}, aapki quotation {quotation.quote_number} ready hai. "
        f"Amount: Rs {quotation.final_amount}. Valid Till: {quotation.valid_till.strftime('%d %b, %I:%M %p')}. "
        f"- Ghidora Transport"
    )
    wa_number = quotation.phone if quotation.phone.startswith('91') else '91' + quotation.phone
    wa_link = f"https://wa.me/{wa_number}?text={wa_text}"

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept' and quotation.status == 'Pending':
            if quotation.needs_admin_approval and not quotation.is_approved:
                messages.warning(request, "Ye quotation admin approval ke intezaar me hai. Thodi der baad try karein.")
            else:
                booking = Booking.objects.create(
                    name=quotation.name,
                    phone=quotation.phone,
                    email=quotation.email,
                    pickup=quotation.pickup,
                    destination=quotation.destination,
                    journey_date=quotation.created_at.date(),
                    distance=quotation.distance,
                    distance_source='Manual Entered',
                    fare=quotation.final_amount,
                    vehicle_type=quotation.vehicle_type,
                    trip_type='One Way',
                )
                quotation.status = 'Accepted'
                quotation.converted_booking = booking
                quotation.save()
                messages.success(request, f"Quotation accept ho gaya! Aapki booking ID: {booking.booking_id}")

        elif action == 'reject':
            quotation.status = 'Rejected'
            quotation.rejection_reason = request.POST.get('reason', 'Not specified')
            quotation.save()
            messages.info(request, "Quotation reject kar diya gaya.")

        return redirect('quotations:quote_detail', quote_number=quotation.quote_number)

    return render(request, 'quotations/quote_detail.html', {
        'quotation': quotation,
        'wa_link': wa_link,
    })


def quote_pdf(request, quote_number):
    quotation = get_object_or_404(Quotation, quote_number=quote_number)
    buffer = generate_quotation_pdf(quotation)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=Quotation_{quotation.quote_number}.pdf'
    return response


# ---------------------------------------------------------------------
# ADMIN SIDE
# ---------------------------------------------------------------------

@staff_member_required
def admin_quote_list(request):
    quotations = Quotation.objects.all().order_by('-created_at')

    for q in quotations:
        if q.is_expired_now:
            q.status = 'Expired'
            q.save(update_fields=['status'])

    context = {
        'quotations': quotations,
        'pending': quotations.filter(status='Pending').count(),
        'accepted': quotations.filter(status='Accepted').count(),
        'rejected': quotations.filter(status='Rejected').count(),
        'expired': quotations.filter(status='Expired').count(),
        'threshold': ADMIN_APPROVAL_THRESHOLD,
    }
    return render(request, 'quotations/admin_quote_list.html', context)


@staff_member_required
def admin_quote_create(request):
    """Admin khud custom quotation bana kar customer ko bhej sakta hai (bade/special loads ke liye)."""
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.quote_type = 'Custom'
            quotation.save()
            messages.success(request, f"Custom quotation {quotation.quote_number} ban gaya.")
            return redirect('quotations:admin_quote_detail', pk=quotation.pk)
    else:
        form = QuoteRequestForm()

    return render(request, 'quotations/quote_form.html', {'form': form, 'admin_mode': True})


@staff_member_required
def admin_quote_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)

    if request.method == 'POST':
        form = AdminQuoteEditForm(request.POST, instance=quotation)
        if form.is_valid():
            form.save()
            messages.success(request, "Quotation update ho gaya.")

            if request.POST.get('resend') == '1':
                sent = _send_quote_email(quotation)
                if sent:
                    messages.success(request, "Naya quote email se bhej diya gaya.")

            return redirect('quotations:admin_quote_detail', pk=quotation.pk)
    else:
        form = AdminQuoteEditForm(instance=quotation)

    wa_text = urllib.parse.quote(
        f"Hello {quotation.name}, aapki quotation {quotation.quote_number} ready hai. "
        f"Amount: Rs {quotation.final_amount}. - Ghidora Transport"
    )
    wa_number = quotation.phone if quotation.phone.startswith('91') else '91' + quotation.phone
    wa_link = f"https://wa.me/{wa_number}?text={wa_text}"

    return render(request, 'quotations/admin_quote_detail.html', {
        'quotation': quotation,
        'form': form,
        'wa_link': wa_link,
    })
