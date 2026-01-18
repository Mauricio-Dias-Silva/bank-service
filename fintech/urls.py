from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'pix/keys', views.PixKeyViewSet, basename='pix-keys')

app_name = 'fintech'

urlpatterns = [
    # MVC Views (Legacy Dashboard)
    path('dashboard/', views.bank_dashboard, name='bank_dashboard'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('iot/', views.iot_dashboard, name='iot_dashboard'),
    path('iot/register/', views.register_device, name='register_device'),
    path('iot/pay/<str:device_id>/', views.simulate_iot_payment, name='simulate_iot_payment'),

    # API Routes (Mobile)
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('app/', views.mobile_app, name='mobile_app_simulator'),
    
    # Swagger Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='fintech:schema'), name='swagger-ui'),
]
