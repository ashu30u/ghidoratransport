from datetime import date
from urllib.parse import quote

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse

from .models import Occasion, OccasionSettings
from .services import (
    sync_upcoming_occasions,
    generate_ai_occasion_message,
    dispatch_occasion_notifications,
    get_occasion_settings
)
from booking.models import Booking


@staff_member_required
def dashboard(request):
    """Smart Occasion Dashboard for Admin Management."""
    today = date.today()

    # Ensure Hareli Tihar exists for 12 Aug 2026
    hareli = Occasion.objects.filter(name__icontains="hareli").first()
    if not hareli:
        Occasion.objects.create(
            name="Hareli Tihar",
            date=today,
            month=today.month,
            day=today.day,
            description="Chhattisgarh First Agricultural Festival",
            source="automatic",
            status="pending_approval",
            approval_status="pending",
            message="Ghidora Transport की ओर से आपको एवं आपके परिवार को हरेली तिहार की हार्दिक शुभकामनाएं। यह पावन पर्व आपके जीवन में सुख, समृद्धि और खुशियां लेकर आए।",
            ai_message="Ghidora Transport की ओर से आपको एवं आपके परिवार को हरेली तिहार की हार्दिक शुभकामनाएं। यह पावन पर्व आपके जीवन में सुख, समृद्धि और खुशियां लेकर आए।",
            is_active=True
        )

    all_occasions = Occasion.objects.filter(is_active=True).order_by('date')

    # Categorize occasions clearly for Admin
    this_month_occasions = all_occasions.filter(date__month=today.month, date__year=today.year)
    upcoming_future_occasions = all_occasions.filter(date__gt=today).exclude(id__in=this_month_occasions.values_list('id', flat=True))
    past_occasions = all_occasions.filter(date__lt=today).exclude(id__in=this_month_occasions.values_list('id', flat=True))

    upcoming_count = all_occasions.filter(date__gte=today).count()
    pending_approval_count = all_occasions.filter(approval_status='pending').count()
    ai_ready_count = all_occasions.exclude(ai_message='').count()
    scheduled_count = all_occasions.filter(status='scheduled').count()
    sent_count = all_occasions.filter(status='sent').count()
    failed_count = all_occasions.filter(status='failed').count()

    return render(request, 'occasions/dashboard.html', {
        'all_occasions': all_occasions,
        'this_month_occasions': this_month_occasions,
        'upcoming_future_occasions': upcoming_future_occasions,
        'past_occasions': past_occasions,
        'current_month_name': today.strftime("%B %Y"),
        'upcoming_count': upcoming_count,
        'pending_approval_count': pending_approval_count,
        'ai_ready_count': ai_ready_count,
        'scheduled_count': scheduled_count,
        'sent_count': sent_count,
        'failed_count': failed_count,
        'settings': get_occasion_settings(),
    })


@staff_member_required
def settings_view(request):
    """Automation Settings Page for Smart Occasion System."""
    setting = get_occasion_settings()

    if request.method == 'POST':
        setting.auto_sync_enabled = request.POST.get('auto_sync_enabled') == 'on'
        setting.advance_import_days = int(request.POST.get('advance_import_days', 30))
        setting.ai_generation_enabled = request.POST.get('ai_generation_enabled') == 'on'
        setting.admin_approval_required = request.POST.get('admin_approval_required') == 'on'
        setting.auto_sending_enabled = request.POST.get('auto_sending_enabled') == 'on'
        setting.customer_sending_enabled = request.POST.get('customer_sending_enabled') == 'on'
        setting.duplicate_protection_enabled = request.POST.get('duplicate_protection_enabled') == 'on'
        setting.save()

        messages.success(request, "Smart Occasion Automation Settings updated successfully.")
        return redirect('occasions_settings')

    return render(request, 'occasions/settings.html', {'setting': setting})


@staff_member_required
def sync_now(request):
    """Manual action to sync Google Calendar upcoming occasions."""
    res = sync_upcoming_occasions()
    messages.success(request, f"Google Calendar Sync Completed: {res.get('imported', 0)} new occasion(s) imported.")
    return redirect('occasions_dashboard')


@staff_member_required
def approve_occasion(request, occasion_id):
    """Approve an occasion and mark ready for scheduling/sending."""
    occ = get_object_or_404(Occasion, id=occasion_id)
    occ.approval_status = 'approved'
    occ.status = 'approved'
    occ.save()
    messages.success(request, f"'{occ.name}' approved successfully.")
    return redirect('occasions_dashboard')


@staff_member_required
def reject_occasion(request, occasion_id):
    """Reject or skip an occasion."""
    occ = get_object_or_404(Occasion, id=occasion_id)
    occ.approval_status = 'rejected'
    occ.status = 'rejected'
    occ.save()
    messages.warning(request, f"'{occ.name}' rejected/skipped.")
    return redirect('occasions_dashboard')


@staff_member_required
def generate_ai_message_view(request, occasion_id):
    """Regenerate AI message for an occasion."""
    occ = get_object_or_404(Occasion, id=occasion_id)
    generate_ai_occasion_message(occ)
    messages.success(request, f"AI greeting message generated for '{occ.name}'.")
    return redirect('occasions_dashboard')


@staff_member_required
def send_occasion_now(request, occasion_id):
    """Trigger immediate sending of an occasion to customers."""
    occ = get_object_or_404(Occasion, id=occasion_id)
    res = dispatch_occasion_notifications(occ, force=True)
    if res.get("sent", 0) > 0:
        messages.success(request, f"'{occ.name}' sent to {res['sent']} customers.")
    else:
        messages.error(request, f"Failed to send '{occ.name}': {res.get('error')}")
    return redirect('occasions_dashboard')


@staff_member_required
def occasion_preview(request, occasion_id):
    """Preview an occasion greeting card modal."""
    occ = get_object_or_404(Occasion, id=occasion_id)
    return render(request, 'occasions/preview_modal.html', {'occasion': occ})


@staff_member_required
def whatsapp_links(request, occasion_id):
    """Existing WhatsApp customer link generator."""
    occasion = get_object_or_404(Occasion, id=occasion_id)
    message = occasion.message or occasion.ai_message or f"Happy {occasion.name} from Ghidora Transport!"

    from quotations.models import Quotation

    booking_customers = list(
        Booking.objects
        .exclude(phone__isnull=True)
        .exclude(phone__exact='')
        .values('name', 'phone')
    )
    quote_customers = list(
        Quotation.objects
        .exclude(phone__isnull=True)
        .exclude(phone__exact='')
        .values('name', 'phone')
    )

    customers = booking_customers + quote_customers

    customer_links = []
    seen_phones = set()
    for c in customers:
        phone = c['phone'].strip().replace(' ', '').replace('-', '')
        if phone in seen_phones:
            continue
        seen_phones.add(phone)

        if not phone.startswith('+'):
            phone = '91' + phone.lstrip('0')
        else:
            phone = phone.replace('+', '')

        wa_link = f"https://wa.me/{phone}?text={quote(message)}"
        customer_links.append({
            'name': c['name'],
            'phone': c['phone'],
            'link': wa_link,
        })

    return render(request, 'occasions/whatsapp_links.html', {
        'occasion': occasion,
        'customer_links': customer_links,
    })