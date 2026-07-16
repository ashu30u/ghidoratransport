from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, Review


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'booking_id',
        'name',
        'phone',
        'email',
        'vehicle_type',
        'trip_type',
        'pickup',
        'destination',
        'journey_date',
        'distance',
        'distance_source',
        'fare',
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
        ("Distance & Fare", {
            "fields": (
                "distance",
                "distance_source",
                "fare",
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

    readonly_fields = ('booking_id',)

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
        "booking",
        "rating_stars",
        "review",
        "created_at",
    )

    search_fields = (
        "booking__booking_id",
        "booking__name",
        "review",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    ordering = ("-created_at",)

    def rating_stars(self, obj):
        return "⭐" * obj.rating

    rating_stars.short_description = "Rating"