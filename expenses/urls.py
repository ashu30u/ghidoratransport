from django.urls import path
from . import views

urlpatterns = [
    path('admin-panel/profit-report/', views.profit_report, name='profit_report'),
]