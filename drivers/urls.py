from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('admin-panel/drivers/', views.driver_list, name='driver_list'),
    path('admin-panel/drivers/add/', views.driver_add, name='driver_add'),
    path('admin-panel/drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('admin-panel/drivers/<int:pk>/', views.driver_detail, name='driver_detail'),
    path('admin-panel/drivers/<int:pk>/make-default/', views.make_default_driver, name='make_default_driver'),
    
]
