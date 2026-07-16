from django.contrib import admin
from django.utils.html import format_html
from .models import Driver, Vehicle


class VehicleInline(admin.StackedInline):
    model = Vehicle
    extra = 0
    max_num = 1


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    inlines = [VehicleInline]

    list_display = (
        'photo_thumb', 'name', 'mobile', 'vehicle_info',
        'status_badge', 'is_default', 'experience_years',
    )
    list_filter = ('status', 'is_default')
    search_fields = ('name', 'mobile', 'license_number')
    list_editable = ()  # status change list se seedha edit page se hi (safer)
    actions = ['mark_available', 'mark_busy', 'make_default_driver']

    fieldsets = (
        ("Driver Details", {
            'fields': ('name', 'mobile', 'photo', 'license_number', 'address', 'experience_years')
        }),
        ("Assignment", {
            'fields': ('status', 'is_default'),
            'description': "Sirf ek driver 'Default' ho sakta hai — usi ko naye bookings auto-assign honge."
        }),
    )

    def photo_thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;width:40px;border-radius:50%;object-fit:cover;" />', obj.photo.url)
        return "—"
    photo_thumb.short_description = "Photo"

    def vehicle_info(self, obj):
        v = obj.vehicle
        if v:
            return f"🚚 {v.vehicle_type} ({v.vehicle_number})"
        return "No vehicle added"
    vehicle_info.short_description = "Vehicle"

    def status_badge(self, obj):
        color = "#16a34a" if obj.status == "available" else "#dc2626"
        return format_html('<b style="color:{}">{}</b>', color, obj.get_status_display())
    status_badge.short_description = "Status"

    @admin.action(description="Selected drivers ko Available mark karo")
    def mark_available(self, request, queryset):
        queryset.update(status='available')

    @admin.action(description="Selected drivers ko Busy mark karo")
    def mark_busy(self, request, queryset):
        queryset.update(status='busy')

    @admin.action(description="Is driver ko Default (permanent auto-assign) banao")
    def make_default_driver(self, request, queryset):
        driver = queryset.first()
        if driver:
            driver.is_default = True
            driver.save()


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'vehicle_number', 'vehicle_type', 'capacity', 'rc_number')
    search_fields = ('vehicle_number', 'rc_number')
