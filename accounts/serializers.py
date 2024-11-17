from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now, timedelta
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from accounts.tasks import send_email_accounts_task
from accounts.utils.client.get_client_info import get_client_info
from accounts.utils.location.get_location_info import get_location_info

from .models import PasswordResetCode
import random
import logging

logger = logging.getLogger(__name__)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")
        
        if not user.is_active:
            raise serializers.ValidationError("Esta conta está inativa.")

        refresh = RefreshToken.for_user(user)

        request = self.context.get('request')
        client_info = get_client_info(request)
        location_info = get_location_info(request.META.get('REMOTE_ADDR'))

        logger.info(f"Usuário {user.email} autenticado. Dispositivo: {client_info}, Localização: {location_info}")

        send_email_accounts_task.delay(
            "Tentativa de login",
            f"Tentativa de login detectada. Dispositivo: {client_info}, Localização: {location_info}",
            [user.email]
        )

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Este e-mail já está registrado.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        subject = "Bem-vindo!"
        message = f"Olá {user.first_name}, obrigado por se registrar!"
        send_email_accounts_task.delay(subject, message, [user.email])

        logger.info(f"Usuário registrado com sucesso: {user.email}")
        return user


class UserRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            # Mensagem genérica para evitar enumeração de e-mails
            raise serializers.ValidationError("Se o e-mail existir, um código de recuperação será enviado.")

        otp_code = f"{random.randint(100000, 999999)}"
        PasswordResetCode.objects.create(
            user=user,
            code=otp_code,
            expires_at=now() + timedelta(minutes=10)
        )

        # Envia o e-mail de forma assíncrona usando Celery
        send_email_accounts_task.delay(
            "Código de Recuperação",
            f"Seu código OTP é: {otp_code}",
            [user.email]
        )

        return value

    def validate(self, attrs):
        # Inclui uma mensagem de sucesso
        return {"message": "Se o e-mail existir, um código de recuperação será enviado."}


class OtpValidateSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        otp_code = attrs['otp']
        otp_entry = PasswordResetCode.objects.filter(code=otp_code).first()

        if not otp_entry or not otp_entry.is_valid():
            raise serializers.ValidationError("OTP inválido ou expirado.")
        
        otp_entry.is_active = False
        otp_entry.save()  # Garantir que não possa ser reutilizado

        return {'message': "OTP válido.", 'user_id': otp_entry.user.id}


class UserResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("As senhas não correspondem.")
        return attrs

    def save(self, user):
        user.set_password(self.validated_data['password'])
        user.save()
        return {"message": "Senha redefinida com sucesso."}
