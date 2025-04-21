from rest_framework import viewsets
from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer

User = get_user_model()

class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer