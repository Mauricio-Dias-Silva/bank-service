from django.urls import path
from . import views

app_name = 'fintech'

urlpatterns = [
    path('', views.bank_dashboard, name='bank_dashboard'),
    path('transfer/', views.transfer_view, name='transfer'),
    
    # IoT / Lazarus
    path('iot/', views.iot_dashboard, name='iot_dashboard'),
    path('iot/register/', views.register_device, name='register_device'),
    path('iot/pay/<str:device_id>/', views.simulate_iot_payment, name='simulate_iot_payment'),
]
