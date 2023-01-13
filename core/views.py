from rest_framework import generics, status, permissions
from django.contrib.auth import login, logout
from rest_framework.response import Response

from core.models import User
from core.serializers import CreateUserSerializer, LoginSerializer, ProfileSerializer, UpdatePasswordSerializer


class SignupView(generics.CreateAPIView):
    """
    Регистрация пользователя
    """
    serializer_class = CreateUserSerializer


class LoginView(generics.CreateAPIView):
    """
    Авторизация пользователя
    """
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = serializer.save()
        login(request=self.request, user=user)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Профиль пользователя. Просмотр, обновление, logout
    """
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(generics.UpdateAPIView):
    """
    Смена пароля пользователя
    """
    serializer_class = UpdatePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
