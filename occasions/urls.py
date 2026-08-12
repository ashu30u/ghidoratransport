from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='occasions_dashboard'),
    path('settings/', views.settings_view, name='occasions_settings'),
    path('toggle-website-banner/', views.toggle_website_banner, name='occasions_toggle_website_banner'),
    path('sync/', views.sync_now, name='occasions_sync'),
    path('approve/<int:occasion_id>/', views.approve_occasion, name='occasions_approve'),
    path('reject/<int:occasion_id>/', views.reject_occasion, name='occasions_reject'),
    path('generate-ai/<int:occasion_id>/', views.generate_ai_message_view, name='occasions_generate_ai'),
    path('send-now/<int:occasion_id>/', views.send_occasion_now, name='occasions_send_now'),
    path('preview/<int:occasion_id>/', views.occasion_preview, name='occasions_preview'),
    path('whatsapp/<int:occasion_id>/', views.whatsapp_links, name='whatsapp_links'),
]