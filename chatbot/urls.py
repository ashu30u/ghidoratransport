from django.urls import path
from . import views

urlpatterns = [
    path("api/chat/", views.chat_endpoint, name="chatbot_chat"),
    path("chatbot/chat/", views.chat_endpoint),
    path("api/confirm-gia-booking/", views.confirm_gia_booking, name="confirm_gia_booking"),
]