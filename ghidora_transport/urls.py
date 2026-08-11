from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
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

    # 🔑 Authentication Routes (3D Login & Logout)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Direct short URL Aliases (/login/ and /logout/)
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.LogoutView.as_view(next_page='login')),

    # Allauth Social Login (Google Auth)
    path('accounts/', include('allauth.urls')),
]

# 🌟 Media & Static Files Access (Development Mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)