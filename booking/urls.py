from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

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

    path('about/', views.about, name='about'),

    path('services/', views.services, name='services'),

    path('card/', views.business_card, name='business_card'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)