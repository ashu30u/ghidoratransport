from datetime import date
from django.contrib import admin
from django.utils.html import format_html
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


@admin.action(description="🚀 Send Now to Customers")
def send_now_action(modeladmin, request, queryset):
    for occ in queryset:
        res = dispatch_occasion_notifications(occ, force=True)
        if res.get("sent", 0) > 0:
            modeladmin.message_user(request, f"Sent '{occ.name}' to {res['sent']} customers.")
        else:
            modeladmin.message_user(request, f"Failed to send '{occ.name}': {res.get('error')}", level="warning")


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


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'source_badge', 'approval_badge', 'has_ai_message', 'has_poster', 'is_active', 'last_sent_year', 'action_buttons')
    list_filter = ('source', 'approval_status', 'status', 'is_active', 'date')
    search_fields = ('name', 'description', 'message', 'ai_message')
    date_hierarchy = 'date'
    actions = [
        generate_ai_message_action,
        approve_occasions_action,
        reject_occasions_action,
        send_now_action,
        whatsapp_links_action,
        sync_google_calendar_action
    ]

    fieldsets = (
        ("📌 Occasion Details", {
            'fields': ('name', 'date', 'description', 'source', 'external_event_id', 'is_active')
        }),
        ("💬 Messaging & AI Generator", {
            'fields': ('ai_message', 'message', 'poster')
        }),
        ("🛡️ Admin Approval & Schedule", {
            'fields': ('approval_status', 'status', 'scheduled_at', 'sent_at', 'last_sent_year')
        }),
    )

    def source_badge(self, obj):
        colors = {
            'google_calendar': '#0284c7',
            'automatic': '#7c3aed',
            'manual': '#059669',
        }
        color = colors.get(obj.source, '#475569')
        return format_html(
            '<span style="background:{}; color:#fff; padding:4px 8px; border-radius:6px; font-weight:700; font-size:11px;">{}</span>',
            color, obj.get_source_display()
        )
    source_badge.short_description = "Source"

    def approval_badge(self, obj):
        colors = {
            'approved': '#10b981',
            'pending': '#f59e0b',
            'rejected': '#ef4444',
        }
        color = colors.get(obj.approval_status, '#64748b')
        return format_html(
            '<span style="background:{}; color:#fff; padding:4px 8px; border-radius:6px; font-weight:700; font-size:11px;">{}</span>',
            color, obj.get_approval_status_display()
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
            '<a class="button" href="/occasions/dashboard/" style="margin-right:5px; background:#0284c7; color:#fff;">Dashboard</a>'
            '<a class="button" href="/occasions/preview/{}/" target="_blank" style="background:#7c3aed; color:#fff;">Preview</a>',
            obj.id
        )
    action_buttons.short_description = "Actions"


@admin.register(OccasionSettings)
class OccasionSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'auto_sync_enabled', 'advance_import_days', 'ai_generation_enabled', 'admin_approval_required', 'auto_sending_enabled', 'customer_sending_enabled')