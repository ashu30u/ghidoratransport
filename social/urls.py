from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    # 🔑 Authentication Endpoints (for 3D login.html)
    path("auth/password-login/", views.password_login, name="password_login"),
    path("auth/request-otp/", views.request_otp, name="request_otp"),
    path("auth/self-signup/", views.self_signup, name="self_signup"),
    path("auth/verify-otp/", views.verify_otp, name="verify_otp"),
    path("auth/set-credentials/", views.set_credentials, name="set_credentials"),

    # 📱 Social Feed & Posts
    path("", views.feed, name="feed"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/like/", views.like_toggle, name="like_toggle"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),

    # 👤 User Profile (Note: 'edit' is placed before '<str:username>' for clean routing)
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
]