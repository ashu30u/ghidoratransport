from datetime import date
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Occasion, OccasionSettings
from .services import generate_ai_occasion_message, dispatch_occasion_notifications, sync_upcoming_occasions


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


@admin.action(description="🚀 Send Now to Customers (Instant Background Dispatch)")
def send_now_action(modeladmin, request, queryset):
    import threading
    count = 0
    for occ in queryset:
        threading.Thread(
            target=dispatch_occasion_notifications,
            args=(occ,),
            kwargs={'force': True},
            daemon=True
        ).start()
        count += 1
    modeladmin.message_user(request, f"🚀 Instant Background Dispatch Triggered for {count} occasion(s)! Email greetings are delivering right now.")


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


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'source_badge', 'approval_badge', 'website_status_badge', 'is_active', 'last_sent_year', 'action_buttons')
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

    fieldsets = (
        ("📌 Occasion Details & Website Status", {
            'fields': ('name', 'date', 'description', 'source', 'is_active', 'external_event_id'),
            'description': "Set 'Is Active' to ON (checked) to display this occasion banner on the website."
        }),
        ("💬 Messaging & AI Generator", {
            'fields': ('ai_message', 'message', 'poster')
        }),
        ("🛡️ Admin Approval & Schedule", {
            'fields': ('approval_status', 'status', 'scheduled_at', 'sent_at', 'last_sent_year')
        }),
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