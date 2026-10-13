from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic.base import RedirectView
from .views import health_check

from booking.views import forgot_password_view

urlpatterns = [
    # Health Check Endpoint for Render & UptimeRobot Monitoring
    path('health', health_check, name='health_check_no_slash'),
    path('health/', health_check, name='health_check'),

    path('favicon.ico', RedirectView.as_view(url='/static/images/logo5.jpeg', permanent=True)),
    # Admin Panel
    path('admin/', admin.site.urls),

    # App Routing
    path('', include('booking.urls')),
    path('', include('drivers.urls')),
    path('', include('chatbot.urls')),
    path('', include('expenses.urls')),
    path('occasions/', include('occasions.urls')),
    path('', include('quotations.urls')),
    path('social/', include('social.urls')),
    path('payments/', include('payments.urls')),
    path('pickupwala/', include('pickupwala.urls')),

    # Universal Mobile & Email OTP Password Reset
    path('accounts/password/reset/', forgot_password_view, name='account_reset_password'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/', forgot_password_view, name='reset_password'),

    # Allauth Social Login & Account Routes (Google Auth, Signup, Login)
    path('accounts/', include('allauth.urls')),

    # Direct short URL Aliases (/login/, /signup/, and /logout/)
    path('login/', allauth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('signup/', allauth_views.SignupView.as_view(template_name='account/signup.html'), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

from pickupwala.views import ranged_media_serve

# 🌟 Media & Static Files Access (Development Mode with Byte Range Seeking Support)
if settings.DEBUG:
    urlpatterns.insert(0, path('media/<path:path>', ranged_media_serve, name='ranged_media_serve'))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)