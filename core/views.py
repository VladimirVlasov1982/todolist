from rest_framework import viewsets, generics

from core.models import User
from core.serializers import ProfileSerializer, CreateUserSerializer


class ProfileView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer


class SignupView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
