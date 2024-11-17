from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from api.views import DeviceViewSet, EquipmentViewSet, MaintenanceViewSet, MaintenanceResetLogViewSet, EmployeeViewSet
from accounts.views import LoginViewSet, RegisterViewSet, RecoveryViewSet
from rest_framework_simplejwt.views import ( TokenVerifyView, TokenBlacklistView)


schema_view = get_schema_view(
    openapi.Info(
        title="API Smartlogger",
        default_version='v1',
        description="Documentation for the API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@injetect.com.br"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'equipments', EquipmentViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'maintenance-reset-logs', MaintenanceResetLogViewSet, basename='maintenance-reset-log')
router.register(r'employees', EmployeeViewSet)
router.register(r'login', LoginViewSet, basename='login')
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'recovery', RecoveryViewSet, basename='recovery')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/', include(router.urls)),
    path('api/', include('accounts.urls')),
    path('api/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
