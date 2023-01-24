from rest_framework import permissions

from goals.models import BoardParticipant


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = 'Вы не являетесь владельцем'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class BoardPermissions(permissions.BasePermission):
    message = 'Вы не являетесь владельцем доски'

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user_id=request.user.id,
                board=obj,
            ).exists()
        return BoardParticipant.objects.filter(
            user_id=request.user.id,
            board=obj,
            role=BoardParticipant.Role.owner,
        ).exists()
