from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from core.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    password_repeat = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat']

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError({'password_repeat': 'Passwords must match'})
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
