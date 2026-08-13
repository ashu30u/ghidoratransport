from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path, include

urlpatterns = [

    path('', views.home, name='home'),

    path(
        'status/',
        views.check_status,
        name='status'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'history/',
        views.booking_history,
        name='history'
    ),

    path(
        'analytics/',
        views.analytics,
        name='analytics'
    ),

    path(
        "manage-bookings/",
        views.manage_bookings,
        name="manage_bookings"
    ),

    path(
        "delete-booking/<int:booking_id>/",
        views.delete_booking,
        name="delete_booking"
    ),

    path(
        "review/<int:booking_id>/",
        views.add_review,
        name="add_review"
    ),

    path(
        "receipt/<int:booking_id>/",
        views.download_receipt,
        name="download_receipt"
    ),

    path(
        "api/calculate-distance/",
        views.calculate_distance_api,
        name="calculate_distance_api"
    ),
    path(
        "api/check-route-fare/",
        views.check_route_fare_api,
        name="check_route_fare_api"
    ),

    path('about/', views.about, name='about'),

    path('services/', views.services, name='services'),

    path('card/', views.business_card, name='business_card'),

    path('contact/', views.contact_us, name='contact_us'),

    path('control-tower/', views.control_tower, name='control_tower'),
    path('api/review/<int:review_id>/like/', views.toggle_review_like, name='toggle_review_like'),
    path('api/review/<int:review_id>/comment/', views.add_review_comment, name='add_review_comment'),
    path('api/review/<int:review_id>/share/', views.record_review_share, name='record_review_share'),
    path('api/submit-user-review/', views.submit_user_review, name='submit_user_review'),
    path('api/export-bookings/', views.export_bookings_api, name='export_bookings_api'),
    path('api/export-reviews/', views.export_reviews_api, name='export_reviews_api'),
    path('pickupwala/', include('pickupwala.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)