from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, Review, BookingAttachment, ContactMessage, PredefinedRouteFare, PredefinedRouteDistance


@admin.register(PredefinedRouteDistance)
class PredefinedRouteDistanceAdmin(admin.ModelAdmin):
    list_display = (
        'from_location',
        'to_location',
        'distance_km_formatted',
        'same_direction_both',
        'colored_status',
        'description',
        'updated_at',
    )

    search_fields = (
        'from_location',
        'to_location',
        'description',
    )

    list_filter = (
        'is_active',
        'same_direction_both',
        'created_at',
        'updated_at',
    )

    ordering = ('from_location', 'to_location')
    list_per_page = 25

    fieldsets = (
        ("📍 Route Locations", {
            "fields": ("from_location", "to_location", "same_direction_both"),
            "description": "Define pickup location, drop location, and whether same distance applies for reverse direction (⇄)."
        }),
        ("📏 Fixed Route Distance", {
            "fields": ("distance_km",),
            "description": "Set exact route distance in KM (e.g. 49.5)."
        }),
        ("⚙️ Status & Description", {
            "fields": ("is_active", "description")
        }),
    )

    actions = ["activate_distances", "deactivate_distances"]

    def distance_km_formatted(self, obj):
        return f"{obj.distance_km} KM"
    distance_km_formatted.short_description = "Distance (KM)"

    def colored_status(self, obj):
        bg = "#10B981" if obj.is_active else "#EF4444"
        label = "Active" if obj.is_active else "Inactive"
        return format_html(
            '<span style="background:{}; color:#ffffff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px;">{}</span>',
            bg, label
        )
    colored_status.short_description = "Status"

    def activate_distances(self, request, queryset):
        rows = queryset.update(is_active=True)
        self.message_user(request, f"✅ {rows} route distance(s) activated successfully!")
    activate_distances.short_description = "✅ Activate Selected Distances"

    def deactivate_distances(self, request, queryset):
        rows = queryset.update(is_active=False)
        self.message_user(request, f"🔴 {rows} route distance(s) set to Inactive!")
    deactivate_distances.short_description = "🔴 Deactivate Selected Distances"


@admin.register(PredefinedRouteFare)
class PredefinedRouteFareAdmin(admin.ModelAdmin):
    list_display = (
        'from_location',
        'to_location',
        'distance_km_formatted',
        'single_fare_formatted',
        'double_fare_formatted',
        'same_direction_both',
        'colored_status',
        'description',
        'updated_at',
    )

    search_fields = (
        'from_location',
        'to_location',
        'description',
    )

    list_filter = (
        'is_active',
        'same_direction_both',
        'created_at',
        'updated_at',
    )

    ordering = ('from_location', 'to_location')
    list_per_page = 25

    fieldsets = (
        ("📍 Route Locations & Distance", {
            "fields": ("from_location", "to_location", "distance_km", "same_direction_both"),
            "description": "Define pickup location, drop location, route distance in KM, and reverse direction mode (⇄)."
        }),
        ("💰 Fixed Fares (Single & Double Trip)", {
            "fields": ("fixed_fare", "double_trip_fare"),
            "description": "Set fixed fare for Single Trip (One Way) and Double Trip (Round Trip). If Double Trip is left blank, system auto-doubles Single Trip fare."
        }),
        ("⚙️ Status & Description", {
            "fields": ("is_active", "description")
        }),
    )

    actions = ["activate_routes", "deactivate_routes"]

    def distance_km_formatted(self, obj):
        if obj.distance_km:
            return f"{obj.distance_km} KM"
        return "-"
    distance_km_formatted.short_description = "Distance (KM)"

    def single_fare_formatted(self, obj):
        return f"₹{obj.fixed_fare:,.0f}"
    single_fare_formatted.short_description = "One-Way Fare (₹)"

    def double_fare_formatted(self, obj):
        if obj.double_trip_fare:
            return f"₹{obj.double_trip_fare:,.0f}"
        return f"₹{obj.fixed_fare * 2:,.0f} (Auto 2x)"
    double_fare_formatted.short_description = "Round-Trip Fare (₹)"

    def colored_status(self, obj):
        bg = "#10B981" if obj.is_active else "#EF4444"
        label = "Active" if obj.is_active else "Inactive"
        return format_html(
            '<span style="background:{}; color:#ffffff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px;">{}</span>',
            bg, label
        )
    colored_status.short_description = "Status"

    def activate_routes(self, request, queryset):
        rows = queryset.update(is_active=True)
        self.message_user(request, f"✅ {rows} route fare(s) activated successfully!")
    activate_routes.short_description = "✅ Activate Selected Routes"

    def deactivate_routes(self, request, queryset):
        rows = queryset.update(is_active=False)
        self.message_user(request, f"🔴 {rows} route fare(s) set to Inactive!")
    deactivate_routes.short_description = "🔴 Deactivate Selected Routes"


class BookingAttachmentInline(admin.TabularInline):
    model = BookingAttachment
    extra = 0
    readonly_fields = ('attachment_type', 'file', 'uploaded_at', 'preview')

    def preview(self, obj):
        if not obj.file:
            return "-"

        if obj.attachment_type == 'voice':
            return format_html(
                '<audio controls src="{}"></audio>', obj.file.url
            )
        elif obj.attachment_type == 'photo':
            return format_html(
                '<img src="{}" style="max-height:120px; border-radius:6px;" />',
                obj.file.url
            )
        elif obj.attachment_type == 'video':
            return format_html(
                '<video controls src="{}" style="max-height:120px;"></video>',
                obj.file.url
            )
        return "-"

    preview.short_description = "Preview"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    inlines = [BookingAttachmentInline]

    list_display = (
        'booking_id',
        'name',
        'direct_call_button',
        'email',
        'vehicle_type',
        'trip_type',
        'pickup',
        'destination',
        'journey_date',
        'distance',
        'duration_text',
        'distance_source',
        'formatted_fare_type',
        'gmaps_nav_link',
        'toll_charges',
        'parking_charges',
        'colored_status',
        'whatsapp_link',
        'booking_date'
    )

    search_fields = (
        'booking_id',
        'name',
        'phone',
        'email',
        'pickup',
        'destination'
    )

    list_filter = (
        'fare_type',
        'vehicle_type',
        'trip_type',
        'status',
        'distance_source',
        'booking_date'
    )

    ordering = ('-booking_date',)

    list_per_page = 20

    fieldsets = (
        ("Customer Details", {
            "fields": ("name", "phone", "email")
        }),
        ("Trip Details", {
            "fields": (
                "pickup",
                "destination",
                "journey_date",
                "vehicle_type",
                "trip_type",
            )
        }),
        ("📍 Coordinates & Navigation", {
            "fields": (
                "pickup_lat",
                "pickup_lng",
                "destination_lat",
                "destination_lng",
                "duration_text",
            ),
            "description": "Exact GPS coordinates and driving duration captured via Google Maps Platform / Satellite Engine."
        }),
        ("Cargo Details", {
            "fields": (
                "cargo_type",
                "weight_value",
                "weight_unit",
                "message",
            ),
            "description": "Customer ne booking ke waqt kya bheja hai "
                            "(text ke through). Voice/Photo/Video niche "
                            "'Booking attachments' section me dikhega."
        }),
        ("Distance & Fare", {
            "fields": (
                "distance",
                "distance_source",
                "fare",
                "fare_type",
            )
        }),
        ("Toll & Parking (Admin Only)", {
            "fields": (
                "toll_charges",
                "parking_charges",
                "toll_screenshot",
            ),
            "description": "Ye charges alag-alag jagah alag hote hain, "
                            "isliye khud manually daalein. Agar toll ka "
                            "SMS/payment screenshot hai to proof ke taur "
                            "par upload kar sakte hain."
        }),
        ("Booking Status", {
            "fields": ("status", "booking_id")
        }),
    )

    def gmaps_nav_link(self, obj):
        if obj.pickup_lat and obj.destination_lat:
            origin = f"{obj.pickup_lat},{obj.pickup_lng}"
            dest = f"{obj.destination_lat},{obj.destination_lng}"
        else:
            import urllib.parse
            origin = urllib.parse.quote(obj.pickup or '')
            dest = urllib.parse.quote(obj.destination or '')
        url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}&travelmode=driving"
        return format_html(
            '<a href="{}" target="_blank" style="background:#10B981; color:#fff; padding:3px 8px; border-radius:8px; font-weight:bold; font-size:11px; text-decoration:none; white-space:nowrap;">🗺️ View Route</a>',
            url
        )
    gmaps_nav_link.short_description = "Google Route"

    def formatted_fare_type(self, obj):
        bg = "#10B981" if obj.fare_type == "Predefined Route Fare" else "#3B82F6"
        fare_val = f"{obj.fare:,.0f}" if obj.fare is not None else "0"
        return format_html(
            '<div style="white-space:nowrap;">'
            '<strong>₹{}</strong> — <span style="background:{}; color:#fff; padding:2px 8px; border-radius:10px; font-size:10.5px; font-weight:bold;">{}</span>'
            '</div>',
            fare_val, bg, obj.fare_type or 'Distance Based Fare'
        )
    formatted_fare_type.short_description = "Fare & Fare Type"

    def direct_call_button(self, obj):
        clean_phone = ''.join(filter(str.isdigit, str(obj.phone or '')))
        return format_html(
            '<a href="tel:{}" style="background:#FF6B00; color:#ffffff; padding:5px 10px; border-radius:12px; font-weight:800; font-size:11.5px; text-decoration:none; white-space:nowrap; box-shadow:0 2px 8px rgba(255,107,0,0.35);">📞 Call {}</a>',
            clean_phone, obj.phone
        )
    direct_call_button.short_description = "📞 Call Customer"

    def colored_status(self, obj):

        colors = {
            "Pending": "orange",
            "Confirmed": "green",
            "Completed": "blue",
            "Cancelled": "red"
        }

        return format_html(
            '<strong style="color:{};">{}</strong>',
            colors.get(obj.status, "black"),
            obj.status
        )

    colored_status.short_description = "Status"

    def whatsapp_link(self, obj):

        message = (
            f"Hello {obj.name},%0A%0A"
            f"Your Ghidora Transport booking update 🚚%0A%0A"
            f"Booking ID: {obj.booking_id}%0A"
            f"Journey Date: {obj.journey_date}%0A"
            f"Vehicle: {obj.vehicle_type}%0A"
            f"Trip Type: {obj.trip_type}%0A"
            f"Status: {obj.status}%0A%0A"
            f"Thank you for choosing Ghidora Transport ❤️"
        )

        return format_html(
            '<a href="https://wa.me/91{}?text={}" target="_blank">📱 WhatsApp</a>',
            obj.phone,
            message
        )

    whatsapp_link.short_description = "WhatsApp"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "rating_stars",
        "short_comment",
        "is_approved",
        "is_verified",
        "created_at",
    )

    search_fields = (
        "guest_name",
        "guest_email",
        "guest_phone",
        "booking__booking_id",
        "booking__name",
        "comment",
        "review",
    )

    list_filter = (
        "is_approved",
        "is_verified",
        "rating",
        "created_at",
    )

    ordering = ("-created_at",)
    actions = ["approve_reviews", "unapprove_reviews", "mark_verified", "unmark_verified"]

    def customer_name(self, obj):
        return obj.display_name
    customer_name.short_description = "Customer"

    def rating_stars(self, obj):
        return "⭐" * obj.rating
    rating_stars.short_description = "Rating"

    def short_comment(self, obj):
        txt = obj.comment or obj.review or ""
        return txt[:50] + "..." if len(txt) > 50 else txt
    short_comment.short_description = "Review Text"

    def approve_reviews(self, request, queryset):
        rows = 0
        for rev in queryset:
            rev.is_approved = True
            rev.save()
            rows += 1
        from django.core.cache import cache
        cache.delete("home_reviews_summary_data")
        self.message_user(request, f"✅ {rows} review(s) approved and published on Home Page!")
    approve_reviews.short_description = "✅ Approve Selected Reviews"

    def unapprove_reviews(self, request, queryset):
        rows = 0
        for rev in queryset:
            rev.is_approved = False
            rev.save()
            rows += 1
        from django.core.cache import cache
        cache.delete("home_reviews_summary_data")
        self.message_user(request, f"⏳ {rows} review(s) hidden / set to Pending!")
    unapprove_reviews.short_description = "⏳ Set Selected Reviews to Pending"

    def mark_verified(self, request, queryset):
        rows = queryset.update(is_verified=True)
        from django.core.cache import cache
        cache.delete("home_reviews_summary_data")
        self.message_user(request, f"🟢 {rows} review(s) marked as Verified Customer!")
    mark_verified.short_description = "🟢 Mark as Verified Customer"

    def unmark_verified(self, request, queryset):
        rows = queryset.update(is_verified=False)
        from django.core.cache import cache
        cache.delete("home_reviews_summary_data")
        self.message_user(request, f"⚪ {rows} review(s) un-marked from Verified!")
    unmark_verified.short_description = "⚪ Unmark Verified Status"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "subject", "created_at")
    search_fields = ("name", "phone", "email", "subject", "message")
    ordering = ("-created_at",)
    readonly_fields = ("name", "phone", "email", "subject", "message", "created_at")


from .models import GiaBookingRecord
from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE booking_giabookingrecord ADD COLUMN weight_display VARCHAR(50) DEFAULT '500 kg'")
except Exception as col_err:
    pass

@admin.register(GiaBookingRecord)
class GiaBookingRecordAdmin(admin.ModelAdmin):
    list_display = (
        "booking_id",
        "customer_name",
        "direct_call_actions",
        "pickup",
        "destination",
        "goods_type",
        "weight_display",
        "distance_km",
        "vehicle_assigned",
        "total_fare_formatted",
        "colored_status",
        "created_at"
    )

    search_fields = ("booking_id", "phone", "pickup", "destination", "goods_type", "customer_name")
    list_filter = ("status", "vehicle_assigned", "created_at")
    ordering = ("-created_at",)

    def total_fare_formatted(self, obj):
        return f"₹{obj.total_fare:,.0f}"
    total_fare_formatted.short_description = "Total Fare"

    def direct_call_actions(self, obj):
        clean_phone = ''.join(filter(str.isdigit, str(obj.phone or '')))
        if len(clean_phone) == 10:
            wa_phone = "91" + clean_phone
        else:
            wa_phone = clean_phone

        return format_html(
            '<div style="display:flex; gap:6px; align-items:center;">'
            '<a href="tel:{}" style="background:#FF6B00; color:#ffffff; padding:6px 12px; border-radius:14px; font-weight:800; font-size:12px; text-decoration:none; white-space:nowrap; box-shadow:0 3px 10px rgba(255,107,0,0.35);">📞 Call {}</a>'
            '<a href="https://wa.me/{}" target="_blank" style="background:#25D366; color:#ffffff; padding:6px 12px; border-radius:14px; font-weight:800; font-size:12px; text-decoration:none; white-space:nowrap; box-shadow:0 3px 10px rgba(37,211,102,0.35);">💬 WhatsApp</a>'
            '</div>',
            clean_phone, obj.phone, wa_phone
        )
    direct_call_actions.short_description = "📞 1-Click Action"

    def colored_status(self, obj):
        bg = "#10B981" if obj.status == "Confirmed" else "#F59E0B"
        return format_html(
            '<span style="background:{}; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px;">{}</span>',
            bg, obj.status
        )
    colored_status.short_description = "Status"    