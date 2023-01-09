from rest_framework import viewsets

from core.models import User
from core.serializers import ProfileSerializer


class ProfileView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
