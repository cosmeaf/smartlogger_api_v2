from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserLoginSerializer, UserRegisterSerializer, UserRecoverySerializer, OtpValidateSerializer, UserResetPasswordSerializer


class LoginViewSet(ModelViewSet):
    permission_classes = []
    serializer_class = UserLoginSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterViewSet(ModelViewSet):
    permission_classes = []
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Usuário registrado com sucesso.",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }, status=status.HTTP_201_CREATED)


class RecoveryViewSet(ModelViewSet):
    permission_classes = []
    serializer_class = UserRecoverySerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)



class OtpValidateView(APIView):
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        serializer = OtpValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        serializer = UserResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer.save(user)
        return Response({"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
