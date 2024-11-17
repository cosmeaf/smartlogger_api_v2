from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  OtpValidateView, ResetPasswordView

urlpatterns = [
    path('validate-otp/', OtpValidateView.as_view(), name='validate-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
