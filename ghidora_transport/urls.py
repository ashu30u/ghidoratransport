from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic.base import RedirectView

urlpatterns = [
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

    # Allauth Social Login & Account Routes (Google Auth, Signup, Login)
    path('accounts/', include('allauth.urls')),

    # Direct short URL Aliases (/login/ and /logout/)
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

# 🌟 Media & Static Files Access (Development Mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)