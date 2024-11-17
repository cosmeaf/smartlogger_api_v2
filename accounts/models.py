from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
import random


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.code} ({'ativo' if self.is_active else 'inativo'})"

    def is_valid(self):
        """Verifica se o OTP é válido e não expirou."""
        return self.is_active and now() < self.expires_at

    @classmethod
    def create_otp(cls, user, expiration_minutes=10):
        """Gera e salva um novo OTP para o usuário."""
        return cls.objects.create(
            user=user,
            code=str(random.randint(100000, 999999)),
            expires_at=now() + timedelta(minutes=expiration_minutes)
        )

    def deactivate(self):
        """Desativa o OTP após uso."""
        self.is_active = False
        self.save()


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Password Reset for {self.user.email} - {self.code}"

    def is_valid(self):
        """Verifica se o código de redefinição de senha é válido."""
        return now() < self.expires_at

    @classmethod
    def create_reset_code(cls, user, expiration_minutes=10):
        """Gera e salva um novo código de redefinição de senha."""
        return cls.objects.create(
            user=user,
            code=str(random.randint(100000, 999999)),
            expires_at=now() + timedelta(minutes=expiration_minutes)
        )
