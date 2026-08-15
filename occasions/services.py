import os
import json
import logging
import urllib.request
import urllib.parse
from datetime import date, datetime, timedelta
from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai

from .models import Occasion, OccasionSettings
from booking.models import Booking

logger = logging.getLogger(__name__)

# Key Indian & Chhattisgarh Festivals list for fallback & matching
RELEVANT_KEYWORDS = [
    'diwali', 'deepavali', 'holi', 'raksha bandhan', 'rakhi', 'ganesh chaturthi',
    'durga puja', 'dussehra', 'vijayadashami', 'eid', 'christmas', 'makar sankranti',
    'pongal', 'navratri', 'janmashtami', 'republic day', 'independence day',
    'gandhi jayanti', 'bhai dooj', 'karwa chauth', 'chhatt', 'baisakhi', 'onam',
    # Chhattisgarh specific festivals & regional occasions
    'hareli', 'chherchhera', 'pola', 'teeja', 'rajim kumbh', 'bastar dussehra',
    'gauta', 'suwa'
]

FALLBACK_FESTIVALS_2026 = [
    {"name": "Republic Day", "date": "2026-01-26", "desc": "National Celebration Day"},
    {"name": "Makar Sankranti", "date": "2026-01-14", "desc": "Harvest Festival"},
    {"name": "Maha Shivratri", "date": "2026-02-15", "desc": "Auspicious Hindu Festival"},
    {"name": "Holi", "date": "2026-03-04", "desc": "Festival of Colors"},
    {"name": "Good Friday", "date": "2026-04-03", "desc": "Christian Holiday"},
    {"name": "Eid ul-Fitr", "date": "2026-03-20", "desc": "Islamic Festival"},
    {"name": "Hareli Tihar", "date": "2026-08-12", "desc": "Chhattisgarh First Agricultural Festival"},
    {"name": "Independence Day", "date": "2026-08-15", "desc": "Indian National Independence Day"},
    {"name": "Raksha Bandhan", "date": "2026-08-28", "desc": "Festival of Brother-Sister Bond"},
    {"name": "Janmashtami", "date": "2026-09-04", "desc": "Lord Krishna Birth Celebration"},
    {"name": "Ganesh Chaturthi", "date": "2026-09-14", "desc": "Ganesh Utsav Festival"},
    {"name": "Gandhi Jayanti", "date": "2026-10-02", "desc": "Mahatma Gandhi Birth Anniversary"},
    {"name": "Dussehra", "date": "2026-10-20", "desc": "Vijayadashami Celebration"},
    {"name": "Diwali", "date": "2026-11-08", "desc": "Festival of Lights"},
    {"name": "Chherchhera Tihar", "date": "2026-12-23", "desc": "Chhattisgarh Dan Punya Festival"},
    {"name": "Christmas", "date": "2026-12-25", "desc": "Christmas Celebration"},
]


def get_occasion_settings():
    """Fetch or create global OccasionSettings singleton instance."""
    setting, _ = OccasionSettings.objects.get_or_create(id=1)
    return setting


def get_gemini_model():
    """Load Gemini AI model safely using environment variable or gemini_key.txt file."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            key_file = os.path.join(apps.get_app_config('chatbot').path, "gemini_key.txt")
            if os.path.exists(key_file):
                with open(key_file, "r") as f:
                    api_key = f.read().strip()
        if api_key:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-flash-latest")
    except Exception as e:
        logger.warning(f"Failed to load Gemini AI model: {e}")
    return None


def is_relevant_occasion(name, description=""):
    """Check if the event name or description is a relevant festival/occasion."""
    combined = f"{name} {description}".lower()
    return any(kw in combined for kw in RELEVANT_KEYWORDS)


def generate_ai_occasion_message(occasion):
    """Generate a warm, natural Ghidora Transport greeting message using Gemini AI."""
    model = get_gemini_model()
    if not model:
        # Fallback greeting message if Gemini AI key is unavailable
        fallback_msg = (
            f"Ghidora Transport की ओर से आपको एवं आपके परिवार को {occasion.name} की "
            f"हार्दिक शुभकामनाएं। यह पावन पर्व आपके जीवन में सुख, समृद्धि और खुशियां लेकर आए।"
        )
        occasion.ai_message = fallback_msg
        if not occasion.message:
            occasion.message = fallback_msg
        occasion.save()
        return fallback_msg

    prompt = (
        f"You are the official communications writer for Ghidora Transport (a leading transport & cargo company in Chhattisgarh & India).\n"
        f"Write a warm, respectful, and natural Hindi festival greeting message (3-4 lines) for: '{occasion.name}'.\n"
        f"Example style:\n"
        f"'Ghidora Transport की ओर से आपको एवं आपके परिवार को {occasion.name} की हार्दिक शुभकामनाएं। यह पावन पर्व आपके जीवन में सुख, समृद्धि और खुशियां लेकर आए।'\n"
        f"Do NOT include hashtags, hype emojis overload, or unnatural bot phrases. Focus on customer goodwill and warm wishes."
    )

    try:
        response = model.generate_content(prompt)
        ai_msg = response.text.strip()
        occasion.ai_message = ai_msg
        if not occasion.message:
            occasion.message = ai_msg
        occasion.save()
        return ai_msg
    except Exception as e:
        logger.error(f"Gemini AI error for {occasion.name}: {e}")
        fallback_msg = (
            f"Ghidora Transport की ओर से आपको एवं आपके परिवार को {occasion.name} की "
            f"हार्दिक शुभकामनाएं। यह पावन पर्व आपके जीवन में सुख, समृद्धि और खुशियां लेकर आए।"
        )
        occasion.ai_message = fallback_msg
        if not occasion.message:
            occasion.message = fallback_msg
        occasion.save()
        return fallback_msg


def fetch_google_calendar_events(start_date=None, end_date=None):
    """Fetch events from Google Calendar API or return relevant fallback events."""
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=1)

    g_api_key = os.environ.get("GOOGLE_CALENDAR_API_KEY")
    g_cal_id = os.environ.get("GOOGLE_CALENDAR_ID", "en.indian#holiday@group.v.calendar.google.com")

    events = []

    if g_api_key:
        try:
            time_min = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
            time_max = datetime.combine(end_date, datetime.max.time()).isoformat() + "Z"
            url = (
                f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(g_cal_id)}/events?"
                f"key={g_api_key}&timeMin={urllib.parse.quote(time_min)}&timeMax={urllib.parse.quote(time_max)}"
                f"&singleEvents=true&orderBy=startTime"
            )
            req = urllib.request.Request(url, headers={'User-Agent': 'GhidoraTransport/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for item in data.get('items', []):
                    start_raw = item.get('start', {}).get('date') or item.get('start', {}).get('dateTime')
                    if not start_raw:
                        continue
                    event_date_str = start_raw.split('T')[0]
                    events.append({
                        'id': item.get('id'),
                        'name': item.get('summary', 'Festival'),
                        'date': event_date_str,
                        'description': item.get('description', ''),
                        'source': 'google_calendar'
                    })
        except Exception as e:
            logger.warning(f"Google Calendar API fetch error: {e}")

    # Combine with fallback regional/national festivals within date range
    for fb in FALLBACK_FESTIVALS_2026:
        fb_d = datetime.strptime(fb['date'], '%Y-%m-%d').date()
        if start_date <= fb_d <= end_date:
            events.append({
                'id': f"fallback_{fb['name'].lower().replace(' ', '_')}_{fb['date']}",
                'name': fb['name'],
                'date': fb['date'],
                'description': fb['desc'],
                'source': 'automatic'
            })

    return events


def sync_upcoming_occasions():
    """Automatically import upcoming occasions ~30 days in advance & generate AI messages."""
    settings_obj = get_occasion_settings()
    if not settings_obj.auto_sync_enabled:
        return {"imported": 0, "status": "Disabled in settings"}

    today = date.today()
    end_window = today + timedelta(days=settings_obj.advance_import_days)

    events = fetch_google_calendar_events(today, end_window)
    imported_count = 0

    for ev in events:
        name = ev['name']
        desc = ev.get('description', '')
        ev_id = ev.get('id')
        ev_date_str = ev['date']
        ev_date = datetime.strptime(ev_date_str, '%Y-%m-%d').date()

        # Check relevance
        if not is_relevant_occasion(name, desc):
            continue

        # Prevent duplicates by external_event_id or (name, date)
        existing = Occasion.objects.filter(external_event_id=ev_id).first()
        if not existing:
            existing = Occasion.objects.filter(name__iexact=name, date=ev_date).first()

        if existing:
            # Update date if needed, do not overwrite admin edited message or poster
            continue

        with transaction.atomic():
            send_time = settings_obj.default_sending_time
            sched_dt = datetime.combine(ev_date, send_time) if send_time else datetime.combine(ev_date, datetime.min.time()).replace(hour=8, minute=35)
            new_occ = Occasion.objects.create(
                name=name,
                date=ev_date,
                description=desc,
                source=ev.get('source', 'google_calendar'),
                external_event_id=ev_id,
                scheduled_at=sched_dt,
                status='pending_approval',
                approval_status='pending',
                is_active=True
            )
            imported_count += 1

            # Generate AI Message automatically if enabled
            if settings_obj.ai_generation_enabled:
                generate_ai_occasion_message(new_occ)

    return {"imported": imported_count, "status": "Success"}


def dispatch_occasion_notifications(occasion, force=False):
    """Send occasion greeting email to distinct customer bookings."""
    settings_obj = get_occasion_settings()
    if not settings_obj.customer_sending_enabled and not force:
        return {"sent": 0, "error": "Customer sending disabled in settings"}

    if occasion.approval_status != 'approved' and not force:
        return {"sent": 0, "error": "Admin approval is required before sending"}

    current_year = date.today().year
    if settings_obj.duplicate_protection_enabled and occasion.last_sent_year == current_year and not force:
        return {"sent": 0, "error": f"Occasion already sent for year {current_year}"}

    from quotations.models import Quotation
    from booking.models import Booking, ContactMessage, GiaBookingRecord, Review
    from django.contrib.auth import get_user_model
    try:
        from allauth.account.models import EmailAddress
    except ImportError:
        EmailAddress = None

    # Auto-sync live customer bookings from Render server before collecting email addresses
    try:
        from sync_render_bookings import sync_bookings_from_render
        sync_bookings_from_render()
    except Exception as sync_err:
        logger.warning(f"Live Render customer auto-sync skipped: {sync_err}")

    User = get_user_model()

    raw_emails = set(['ghidoratransport@gmail.com'])

    # 1. Booking Customer Emails
    try:
        for em in Booking.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True):
            if em and em.strip():
                raw_emails.add(em.strip().lower())
    except Exception as e:
        logger.warning(f"Error fetching Booking emails: {e}")

    # 2. Quotation (Get Instant Price Estimate) Customer Emails
    try:
        for em in Quotation.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True):
            if em and em.strip():
                raw_emails.add(em.strip().lower())
    except Exception as e:
        logger.warning(f"Error fetching Quotation emails: {e}")

    # 3. Contact Us Messages Customer Emails
    try:
        for em in ContactMessage.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True):
            if em and em.strip():
                raw_emails.add(em.strip().lower())
    except Exception as e:
        logger.warning(f"Error fetching ContactMessage emails: {e}")

    # 4. Gia AI Booking Records Customer Emails
    try:
        for em in GiaBookingRecord.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True):
            if em and em.strip():
                raw_emails.add(em.strip().lower())
    except Exception as e:
        logger.warning(f"Error fetching GiaBookingRecord emails: {e}")

    # 5. Review Guest Emails
    try:
        for em in Review.objects.exclude(guest_email__isnull=True).exclude(guest_email__exact='').values_list('guest_email', flat=True):
            if em and em.strip():
                raw_emails.add(em.strip().lower())
    except Exception as e:
        logger.warning(f"Error fetching Review emails: {e}")

    # 6. Registered User Account Emails
    try:
        for em in User.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True):
            if em and em.strip():
                raw_emails.add(em.strip().lower())
    except Exception as e:
        logger.warning(f"Error fetching User emails: {e}")

    # 7. Allauth EmailAddress Model Emails
    if EmailAddress:
        try:
            for em in EmailAddress.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True):
                if em and em.strip():
                    raw_emails.add(em.strip().lower())
        except Exception as e:
            logger.warning(f"Error fetching EmailAddress emails: {e}")

    emails = sorted(list(raw_emails))

    if not emails:
        return {"sent": 0, "error": "No customer emails found"}

    subject = f"{occasion.name} Mubarak ho - Ghidora Transport"
    plain_text = occasion.message or occasion.ai_message or f"Happy {occasion.name} from Ghidora Transport!"

    # Safely load poster image bytes once before recipient loop
    img_data = None
    poster_filename = None
    if occasion.poster:
        try:
            occasion.poster.open('rb')
            img_data = occasion.poster.read()
            occasion.poster.close()
            poster_filename = os.path.basename(occasion.poster.name)
        except Exception as img_err:
            logger.error(f"Failed to read occasion poster image: {img_err}")

    if img_data:
        html_body = f"""
        <div style="font-family: Arial, sans-serif; font-size: 15px; color: #333; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px;">
            <h2 style="color: #0284c7; text-align: center;">GHIDORA TRANSPORT</h2>
            <img src="cid:poster_image" style="max-width: 100%; border-radius: 8px;" />
            <p style="margin-top: 15px; white-space: pre-line; line-height: 1.6;">{plain_text}</p>
        </div>
        """
    else:
        html_body = f"""
        <div style="font-family: Arial, sans-serif; font-size: 15px; color: #333; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px;">
            <h2 style="color: #0284c7; text-align: center;">GHIDORA TRANSPORT</h2>
            <p style="margin-top: 15px; white-space: pre-line; line-height: 1.6;">{plain_text}</p>
        </div>
        """

    sent_count = 0
    last_error = None
    for email in emails:
        try:
            mail = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            mail.attach_alternative(html_body, "text/html")

            if img_data:
                from email.mime.image import MIMEImage
                img = MIMEImage(img_data)
                img.add_header('Content-ID', '<poster_image>')
                img.add_header('Content-Disposition', 'inline', filename=poster_filename or 'poster.jpeg')
                mail.attach(img)

            mail.send(fail_silently=False)
            sent_count += 1
            logger.info(f"Successfully sent occasion email to {email}")
            print(f"✅ Sent occasion '{occasion.name}' email to {email}")
        except Exception as e:
            last_error = str(e)
            logger.error(f"Error sending email to {email}: {e}")
            print(f"❌ Error sending email to {email}: {e}")

    if sent_count > 0:
        occasion.last_sent_year = current_year
        occasion.sent_at = datetime.now()
        occasion.status = 'sent'
        occasion.save()
        return {"sent": sent_count, "status": f"Delivered to {sent_count} customer(s)"}
    else:
        occasion.status = 'failed'
        occasion.save()
        err_msg = last_error or "Could not deliver email to any customer."
        return {"sent": 0, "error": f"Failed to send email: {err_msg}"}
