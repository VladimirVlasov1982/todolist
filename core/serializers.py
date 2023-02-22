from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

from core.fields import PasswordField
from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя
    """
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError({'password_repeat': 'Passwords must match'})
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """
    Сериализатор авторизации пользователя
    """
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')
        read_only_fields = ('id', 'first_name', 'last_name', 'email')

    def create(self, validated_data: dict) -> User:
        if not (
                user := authenticate(
                    username=validated_data['username'],
                    password=validated_data['password'],
                )
        ):
            raise AuthenticationFailed
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializer(serializers.Serializer):
    """
    Сериализатор обновления пароля пользователя
    """
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate(self, attrs: dict) -> dict:
        if not self.instance.check_password(attrs['old_password']):
            raise ValidationError({'old_password': 'field is incorrect'})
        return attrs

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance

    def create(self, validated_data: dict):
        raise NotImplementedError
