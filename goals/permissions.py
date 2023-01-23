from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = 'Вы не являетесь владельцем'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
