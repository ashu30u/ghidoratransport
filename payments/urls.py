from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # Customer-facing
    path("pay/<str:payment_id>/", views.customer_payment_page, name="customer_payment_page"),
    path("booking/<str:booking_id>/pay-now/", views.customer_request_payment, name="customer_request_payment"),
    path("history/<str:booking_id>/", views.payment_history, name="payment_history"),
    path("receipt/<str:payment_id>/view/", views.view_receipt, name="view_receipt"),
    path("receipt/<str:payment_id>/download/", views.download_receipt, name="download_receipt"),

    # Admin-facing
    path("admin-panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/create-request/<str:booking_id>/", views.admin_create_payment_request, name="admin_create_payment_request"),
    path("admin-panel/verify/<str:payment_id>/", views.admin_verification_panel, name="admin_verification_panel"),
    path("admin-panel/settings/", views.admin_payment_settings, name="admin_payment_settings"),
] 