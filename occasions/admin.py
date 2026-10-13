from datetime import date, datetime
from django.contrib import admin
from django import forms
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging

from .models import Occasion, OccasionSettings, OccasionRecipient
from .services import generate_ai_occasion_message, dispatch_occasion_notifications, sync_upcoming_occasions

logger = logging.getLogger(__name__)


@admin.action(description="🤖 Generate AI Message for selected occasion(s)")
def generate_ai_message_action(modeladmin, request, queryset):
    count = 0
    for occ in queryset:
        generate_ai_occasion_message(occ)
        count += 1
    modeladmin.message_user(request, f"AI greeting message generated for {count} occasion(s).")


@admin.action(description="✅ Approve Selected Occasion(s)")
def approve_occasions_action(modeladmin, request, queryset):
    updated = queryset.update(approval_status='approved', status='approved')
    modeladmin.message_user(request, f"{updated} occasion(s) approved successfully.")


@admin.action(description="❌ Reject / Skip Selected Occasion(s)")
def reject_occasions_action(modeladmin, request, queryset):
    updated = queryset.update(approval_status='rejected', status='rejected')
    modeladmin.message_user(request, f"{updated} occasion(s) rejected / skipped.")


@admin.action(description="🚀 Send Now to Customers (Instant Dispatch)")
def send_now_action(modeladmin, request, queryset):
    total_delivered = 0
    failed_occasions = []
    for occ in queryset:
        res = dispatch_occasion_notifications(occ, force=True)
        sent = res.get('sent', 0)
        if sent > 0:
            total_delivered += sent
        else:
            failed_occasions.append(f"{occ.name} ({res.get('error', 'Failed')})")

    if total_delivered > 0:
        modeladmin.message_user(
            request,
            f"🚀 Success! Delivered greeting emails to {total_delivered} customer(s)."
        )
    if failed_occasions:
        modeladmin.message_user(
            request,
            f"❌ Failed occasions: {', '.join(failed_occasions)}",
            level="error"
        )


@admin.action(description="💬 View WhatsApp Links")
def whatsapp_links_action(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(request, "Please select exactly ONE occasion to view WhatsApp links.", level="error")
        return
    occasion = queryset.first()
    return HttpResponseRedirect(reverse('whatsapp_links', args=[occasion.id]))


@admin.action(description="🔄 Sync Google Calendar Occasions Now")
def sync_google_calendar_action(modeladmin, request, queryset):
    res = sync_upcoming_occasions()
    modeladmin.message_user(request, f"Synced Google Calendar: {res.get('imported', 0)} new occasion(s) imported.")


@admin.action(description="🟢 Turn ON selected occasion(s) for Website Display")
def turn_on_website_action(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"🟢 {updated} occasion(s) turned ON for Website display.")


@admin.action(description="🔴 Turn OFF selected occasion(s) from Website Display")
def turn_off_website_action(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"🔴 {updated} occasion(s) turned OFF (hidden from Website).")


class Admin12HourSplitDateTimeWidget(forms.Widget):
    """
    Renders a dedicated 12-Hour AM/PM schedule picker:
    - Date field (YYYY-MM-DD)
    - 12-Hour dropdown (01 to 12) - strictly max 12 hours
    - Minute dropdown (00 to 59)
    - AM / PM dropdown (AM, PM)
    - '⚡ Now (Abhi Ka Time)' button
    - '❌ Clear Schedule' button
    - Live Indian Standard Time (IST) schedule badge
    """
    template_name = None

    def format_value(self, value):
        if not value:
            return None
        if isinstance(value, str):
            return value
        local_dt = timezone.localtime(value) if timezone.is_aware(value) else value
        return local_dt

    def render(self, name, value, attrs=None, renderer=None):
        date_str = ""
        hour_val = "10"
        minute_val = "00"
        ampm_val = "AM"
        preview_text = "⚪ Abhi koi schedule set nahi hai (Automatic email send off hai)"

        dt_val = self.format_value(value)
        if dt_val and isinstance(dt_val, (datetime, date)):
            if isinstance(dt_val, datetime):
                date_str = dt_val.strftime('%Y-%m-%d')
                h = dt_val.hour
                h12 = 12 if (h % 12 == 0) else (h % 12)
                hour_val = f"{h12:02d}"
                minute_val = f"{dt_val.minute:02d}"
                ampm_val = "AM" if h < 12 else "PM"
                preview_text = f"⏰ <b>Scheduled For:</b> {dt_val.strftime('%d %b %Y')} at <b>{hour_val}:{minute_val} {ampm_val}</b> (Indian Standard Time)"
            else:
                date_str = dt_val.strftime('%Y-%m-%d')

        # Build Hour options (01 to 12 strictly)
        hour_options = []
        for h in range(1, 13):
            h_str = f"{h:02d}"
            sel = "selected" if h_str == hour_val else ""
            hour_options.append(f'<option value="{h_str}" {sel}>{h_str}</option>')
        hours_html = "\n".join(hour_options)

        # Build Minute options (00 to 59)
        minute_options = []
        for m in range(0, 60):
            m_str = f"{m:02d}"
            sel = "selected" if m_str == minute_val else ""
            minute_options.append(f'<option value="{m_str}" {sel}>{m_str}</option>')
        minutes_html = "\n".join(minute_options)

        am_sel = "selected" if ampm_val == "AM" else ""
        pm_sel = "selected" if ampm_val == "PM" else ""

        html = f"""
        <div id="wrapper_{name}" class="schedule-12hr-card" style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:16px 20px; max-width:720px; box-shadow:0 4px 16px rgba(0,0,0,0.25); font-family:inherit; box-sizing:border-box;">
            <!-- Top Controls Row (Date, 12-Hour Time, and Buttons perfectly aligned) -->
            <div style="display:flex; flex-wrap:wrap; align-items:flex-end; gap:14px;">
                <!-- 1. Date Field -->
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <label style="font-size:11px; font-weight:800; color:#38bdf8; text-transform:uppercase; letter-spacing:0.6px; margin:0;">📅 Date</label>
                    <input type="date" id="{name}_date" name="{name}_date" value="{date_str}" style="height:38px; line-height:38px; background:#1e293b; color:#ffffff; border:1px solid #334155; padding:0 12px; border-radius:8px; font-size:13.5px; font-weight:600; font-family:inherit; outline:none; box-sizing:border-box;" />
                </div>

                <!-- 2. 12-Hour Time Controls -->
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <label style="font-size:11px; font-weight:800; color:#38bdf8; text-transform:uppercase; letter-spacing:0.6px; margin:0;">⏰ Time (12-Hour AM/PM)</label>
                    <div style="display:flex; align-items:center; gap:6px; height:38px;">
                        <!-- Hour 1-12 -->
                        <select id="{name}_hour" name="{name}_hour" style="height:38px; line-height:36px; background:#1e293b; color:#ffffff; border:1px solid #334155; padding:0 8px; border-radius:8px; font-size:14px; font-weight:700; font-family:inherit; cursor:pointer; outline:none; box-sizing:border-box; min-width:56px; text-align:center;">
                            {hours_html}
                        </select>
                        <span style="font-size:18px; font-weight:900; color:#38bdf8; user-select:none; line-height:1;">:</span>
                        <!-- Minute 00-59 -->
                        <select id="{name}_minute" name="{name}_minute" style="height:38px; line-height:36px; background:#1e293b; color:#ffffff; border:1px solid #334155; padding:0 8px; border-radius:8px; font-size:14px; font-weight:700; font-family:inherit; cursor:pointer; outline:none; box-sizing:border-box; min-width:56px; text-align:center;">
                            {minutes_html}
                        </select>
                        <!-- AM/PM -->
                        <select id="{name}_ampm" name="{name}_ampm" style="height:38px; line-height:36px; background:#0284c7; color:#ffffff; border:1px solid #38bdf8; padding:0 10px; border-radius:8px; font-size:13.5px; font-weight:800; font-family:inherit; cursor:pointer; outline:none; box-sizing:border-box; min-width:62px; text-align:center;">
                            <option value="AM" {am_sel}>AM</option>
                            <option value="PM" {pm_sel}>PM</option>
                        </select>
                    </div>
                </div>

                <!-- 3. Quick Action Buttons (Level with inputs) -->
                <div style="display:flex; align-items:center; gap:8px; height:38px;">
                    <button type="button" id="{name}_btn_now" style="height:38px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; padding:0 14px; border-radius:8px; font-size:12px; font-weight:800; font-family:inherit; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 8px rgba(16,185,129,0.3); white-space:nowrap; box-sizing:border-box;">
                        ⚡ Set to Now
                    </button>
                    <button type="button" id="{name}_btn_clear" style="height:38px; background:#334155; color:#cbd5e1; border:1px solid #475569; padding:0 12px; border-radius:8px; font-size:12px; font-weight:700; font-family:inherit; cursor:pointer; white-space:nowrap; box-sizing:border-box;">
                        ❌ Clear
                    </button>
                </div>
            </div>

            <!-- Live Status Preview Badge -->
            <div id="{name}_preview_badge" style="margin-top:14px; background:rgba(2, 132, 199, 0.12); border:1px solid rgba(56, 189, 248, 0.35); padding:9px 14px; border-radius:8px; font-size:13px; color:#38bdf8; font-weight:700; display:flex; align-items:center; gap:8px; box-sizing:border-box;">
                {preview_text}
            </div>

            <!-- Helper Note nested inside card -->
            <div style="margin-top:8px; font-size:11.5px; color:#94a3b8; line-height:1.4;">
                ℹ️ Occasion greeting emails will automatically send to all customers on this date & 12-hour time.
            </div>

            <!-- Hidden input to submit standard datetime value -->
            <input type="hidden" id="{name}" name="{name}" value="{date_str + ' ' + hour_val + ':' + minute_val + ' ' + ampm_val if date_str else ''}" />

            <!-- Script to synchronize values and provide real-time updates -->
            <script>
            (function() {{
                const dateEl = document.getElementById('{name}_date');
                const hourEl = document.getElementById('{name}_hour');
                const minEl = document.getElementById('{name}_minute');
                const ampmEl = document.getElementById('{name}_ampm');
                const hiddenEl = document.getElementById('{name}');
                const previewEl = document.getElementById('{name}_preview_badge');
                const btnNow = document.getElementById('{name}_btn_now');
                const btnClear = document.getElementById('{name}_btn_clear');

                function updatePreview() {{
                    const d = dateEl.value;
                    const h = hourEl.value;
                    const m = minEl.value;
                    const ap = ampmEl.value;

                    if (!d) {{
                        hiddenEl.value = '';
                        previewEl.innerHTML = '<span style="color:#94a3b8;">⚪ Abhi koi schedule set nahi hai (Automatic email send off hai)</span>';
                        return;
                    }}

                    hiddenEl.value = d + ' ' + h + ':' + m + ' ' + ap;

                    try {{
                        const [year, month, day] = d.split('-');
                        const dObj = new Date(year, month - 1, day);
                        const dateFormatted = dObj.toLocaleDateString('en-IN', {{ day: 'numeric', month: 'short', year: 'numeric' }});
                        previewEl.innerHTML = '⏰ <b>Scheduled For:</b> ' + dateFormatted + ' at <b>' + h + ':' + m + ' ' + ap + '</b> (Indian Standard Time)';
                    }} catch (e) {{
                        previewEl.innerHTML = '⏰ <b>Scheduled For:</b> ' + d + ' at ' + h + ':' + m + ' ' + ap + ' (IST)';
                    }}
                }}

                if (dateEl) {{
                    dateEl.addEventListener('change', updatePreview);
                    hourEl.addEventListener('change', updatePreview);
                    minEl.addEventListener('change', updatePreview);
                    ampmEl.addEventListener('change', updatePreview);
                }}

                if (btnNow) {{
                    btnNow.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const now = new Date();
                        const year = now.getFullYear();
                        const month = String(now.getMonth() + 1).padStart(2, '0');
                        const day = String(now.getDate()).padStart(2, '0');
                        dateEl.value = year + '-' + month + '-' + day;

                        let h = now.getHours();
                        const ap = h >= 12 ? 'PM' : 'AM';
                        let h12 = h % 12;
                        if (h12 === 0) h12 = 12;

                        hourEl.value = String(h12).padStart(2, '0');
                        minEl.value = String(now.getMinutes()).padStart(2, '0');
                        ampmEl.value = ap;

                        updatePreview();
                    }});
                }}

                if (btnClear) {{
                    btnClear.addEventListener('click', function(e) {{
                        e.preventDefault();
                        dateEl.value = '';
                        updatePreview();
                    }});
                }}

                // Run on load
                updatePreview();
            }})();
            </script>
        </div>
        """
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        d = data.get(f"{name}_date")
        if not d or not d.strip():
            raw = data.get(name)
            if not raw or not raw.strip():
                return None
            return raw.strip()

        h = data.get(f"{name}_hour", "12")
        m = data.get(f"{name}_minute", "00")
        ap = data.get(f"{name}_ampm", "AM").strip().upper()

        try:
            h_int = int(h)
            m_int = int(m)
            if ap == "PM" and h_int != 12:
                h_int += 12
            elif ap == "AM" and h_int == 12:
                h_int = 0
            return f"{d.strip()} {h_int:02d}:{m_int:02d}:00"
        except Exception:
            return f"{d.strip()} {h}:{m} {ap}"


class OccasionAdminForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=Admin12HourSplitDateTimeWidget(),
        required=False,
        label="Scheduled at",
        help_text=""
    )

    class Meta:
        model = Occasion
        fields = '__all__'


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    form = OccasionAdminForm
    list_display = (
        'name',
        'date',
        'schedule_badge',
        'source_badge',
        'approval_badge',
        'website_status_badge',
        'is_active',
        'last_sent_year',
        'action_buttons'
    )
    list_editable = ('is_active',)
    list_filter = ('is_active', 'source', 'approval_status', 'status', 'date')
    search_fields = ('name', 'description', 'message', 'ai_message')
    date_hierarchy = 'date'
    actions = [
        turn_on_website_action,
        turn_off_website_action,
        generate_ai_message_action,
        approve_occasions_action,
        reject_occasions_action,
        send_now_action,
        whatsapp_links_action,
        sync_google_calendar_action
    ]

    readonly_fields = ('sent_at', 'last_sent_year')

    fieldsets = (
        ("📌 Occasion Details & Website Status", {
            'fields': ('name', 'date', 'description', 'source', 'is_active'),
            'description': "Set 'Is Active' to ON (checked) to display this occasion banner on the website."
        }),
        ("💬 Greeting Message & Poster", {
            'fields': ('message', 'ai_message', 'poster')
        }),
        ("⏰ Approval & Send Schedule (12-Hour AM/PM)", {
            'fields': ('approval_status', 'scheduled_at'),
            'description': "Set Approval status to 'Approved' and choose the exact Date & 12-Hour AM/PM Time to send this greeting."
        }),
        ("🕒 Dispatch History (System Log)", {
            'classes': ('collapse',),
            'fields': ('sent_at', 'last_sent_year'),
            'description': "Automatic system audit records (Read Only)."
        }),
    )

    def schedule_badge(self, obj):
        if not obj.scheduled_at:
            return mark_safe('<span style="color:#64748b; font-size:11px; font-weight:600;">—</span>')
        local_dt = timezone.localtime(obj.scheduled_at)
        time_str = local_dt.strftime('%d %b %Y, %I:%M %p')
        current_year = date.today().year
        if obj.status == 'sent' or obj.last_sent_year == current_year:
            return mark_safe(f'<span style="background:#065f46; color:#a7f3d0; padding:4px 9px; border-radius:10px; font-weight:700; font-size:11px; white-space:nowrap;">✅ Sent ({time_str})</span>')
        elif obj.scheduled_at <= timezone.now():
            return mark_safe(f'<span style="background:#b45309; color:#fef3c7; padding:4px 9px; border-radius:10px; font-weight:700; font-size:11px; white-space:nowrap;">⚡ Due ({time_str})</span>')
        else:
            return mark_safe(f'<span style="background:#1e3a8a; color:#bfdbfe; padding:4px 9px; border-radius:10px; font-weight:700; font-size:11px; white-space:nowrap;">⏳ Scheduled ({time_str})</span>')
    schedule_badge.short_description = "Scheduled (12-Hr AM/PM)"

    def save_model(self, request, obj, form, change):
        if obj.approval_status == 'approved':
            obj.status = 'approved'
        elif obj.approval_status == 'rejected':
            obj.status = 'rejected'
        super().save_model(request, obj, form, change)

        # Immediate dispatch if scheduled time has arrived/passed!
        now = timezone.now()
        current_year = date.today().year
        if obj.approval_status == 'approved' and obj.scheduled_at and obj.scheduled_at <= now and obj.status != 'sent' and obj.last_sent_year != current_year:
            import threading
            def _async_send(occ_id):
                try:
                    from .models import Occasion as OccModel
                    target_occ = OccModel.objects.get(id=occ_id)
                    dispatch_occasion_notifications(target_occ)
                except Exception as err:
                    logger.error(f"Error in async dispatch on save: {err}")
            threading.Thread(target=_async_send, args=(obj.id,), daemon=True).start()
            self.message_user(
                request,
                f"⚡ Scheduled time ({timezone.localtime(obj.scheduled_at).strftime('%I:%M %p')}) is due now. Dispatched greeting to customers in background!"
            )
        elif obj.approval_status == 'approved' and obj.scheduled_at and obj.scheduled_at > now:
            self.message_user(
                request,
                f"⏰ Successfully scheduled for {timezone.localtime(obj.scheduled_at).strftime('%d %b %Y at %I:%M %p')}. It will automatically be sent when this time arrives."
            )


    def website_status_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="background:#10B981; color:#ffffff; padding:4px 10px; border-radius:12px; font-weight:700; font-size:11px; white-space:nowrap; display:inline-block;">🟢 ON</span>')
        return mark_safe('<span style="background:#EF4444; color:#ffffff; padding:4px 10px; border-radius:12px; font-weight:700; font-size:11px; white-space:nowrap; display:inline-block;">🔴 OFF</span>')
    website_status_badge.short_description = "Website Status"

    def source_badge(self, obj):
        colors = {
            'google_calendar': ('#0284c7', '#ffffff'),
            'automatic': ('#7c3aed', '#ffffff'),
            'manual': ('#059669', '#ffffff'),
        }
        bg, fg = colors.get(obj.source, ('#475569', '#ffffff'))
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 10px; border-radius:12px; font-weight:700; font-size:11px; white-space:nowrap; display:inline-block;">{}</span>',
            bg, fg, obj.get_source_display()
        )
    source_badge.short_description = "Source"

    def approval_badge(self, obj):
        colors = {
            'approved': ('#10b981', '#ffffff', '✅ Approved'),
            'pending': ('#f59e0b', '#ffffff', '⏳ Pending Review'),
            'rejected': ('#ef4444', '#ffffff', '❌ Rejected'),
        }
        bg, fg, label = colors.get(obj.approval_status, ('#64748b', '#ffffff', obj.get_approval_status_display()))
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 10px; border-radius:12px; font-weight:700; font-size:11px; white-space:nowrap; display:inline-block;">{}</span>',
            bg, fg, label
        )
    approval_badge.short_description = "Approval Status"

    def has_ai_message(self, obj):
        return bool(obj.ai_message)
    has_ai_message.boolean = True
    has_ai_message.short_description = "AI Message"

    def has_poster(self, obj):
        return bool(obj.poster)
    has_poster.boolean = True
    has_poster.short_description = "Poster"

    def action_buttons(self, obj):
        return format_html(
            '<div style="display:flex; gap:6px; align-items:center; white-space:nowrap;">'
            '<a class="button" href="/occasions/send-now/{}/" style="background:#10b981 !important; color:#ffffff !important; padding:4px 10px !important; border-radius:8px !important; font-weight:700 !important; font-size:11px !important; text-decoration:none !important;" onclick="return confirm(\'Send greeting email to ALL customers now?\');">🚀 Send Now</a>'
            '<a class="button" href="/occasions/dashboard/" style="background:#0284c7 !important; color:#ffffff !important; padding:4px 10px !important; border-radius:8px !important; font-weight:700 !important; font-size:11px !important; text-decoration:none !important;">📊 Dashboard</a>'
            '<a class="button" href="/occasions/preview/{}/" target="_blank" style="background:#7c3aed !important; color:#ffffff !important; padding:4px 10px !important; border-radius:8px !important; font-weight:700 !important; font-size:11px !important; text-decoration:none !important;">👁️ Preview</a>'
            '</div>',
            obj.id, obj.id
        )
    action_buttons.short_description = "Actions"


@admin.register(OccasionSettings)
class OccasionSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'show_on_website', 'website_banner_badge', 'auto_sync_enabled', 'advance_import_days', 'ai_generation_enabled', 'admin_approval_required', 'auto_sending_enabled', 'customer_sending_enabled')
    list_editable = ('show_on_website', 'auto_sync_enabled', 'advance_import_days', 'ai_generation_enabled', 'admin_approval_required', 'auto_sending_enabled', 'customer_sending_enabled')

    def website_banner_badge(self, obj):
        if getattr(obj, 'show_on_website', True):
            return mark_safe('<span style="background:#10B981; color:#fff; padding:4px 10px; border-radius:12px; font-weight:800; font-size:11px;">🟢 ON (Website Display Active)</span>')
        return mark_safe('<span style="background:#EF4444; color:#fff; padding:4px 10px; border-radius:12px; font-weight:800; font-size:11px;">🔴 OFF (Website Display Disabled)</span>')
    website_banner_badge.short_description = "Global Banner Display"


@admin.action(description="🟢 Activate Selected Recipient(s)")
def activate_recipients_action(modeladmin, request, queryset):
    count = queryset.update(is_active=True)
    modeladmin.message_user(request, f"🟢 {count} recipient(s) activated successfully.")


@admin.action(description="🔴 Deactivate Selected Recipient(s)")
def deactivate_recipients_action(modeladmin, request, queryset):
    count = queryset.update(is_active=False)
    modeladmin.message_user(request, f"🔴 {count} recipient(s) deactivated.")


@admin.register(OccasionRecipient)
class OccasionRecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'status_badge', 'is_active', 'notes', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('email', 'name', 'notes')
    list_filter = ('is_active', 'created_at')
    actions = [activate_recipients_action, deactivate_recipients_action]

    fieldsets = (
        ("✉️ Gmail / Email Recipient Details", {
            'fields': ('email', 'name', 'is_active', 'notes'),
            'description': "Add any Gmail or email address here. Whenever an occasion greeting is dispatched, all active emails in this list will automatically receive the greeting email."
        }),
    )

    def status_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="background:#10B981; color:#fff; padding:3px 8px; border-radius:10px; font-weight:700; font-size:11px;">🟢 Active</span>')
        return mark_safe('<span style="background:#EF4444; color:#fff; padding:3px 8px; border-radius:10px; font-weight:700; font-size:11px;">🔴 Inactive</span>')
    status_badge.short_description = "Status"