from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    # Customer side
    path('get-quotation/', views.quote_request, name='quote_request'),
    path('quotation/<str:quote_number>/', views.quote_detail, name='quote_detail'),
    path('quotation/<str:quote_number>/pdf/', views.quote_pdf, name='quote_pdf'),

    # Admin side
    path('admin-panel/quotations/', views.admin_quote_list, name='admin_quote_list'),
    path('admin-panel/quotations/custom/', views.admin_quote_create, name='admin_quote_create'),
    path('admin-panel/quotations/<int:pk>/', views.admin_quote_detail, name='admin_quote_detail'),
]
