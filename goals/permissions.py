from rest_framework import permissions


class IsOwnerCategoryOrNot(permissions.BasePermission):
    message = 'Вы не являетесь владельцем категории'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwnerGoalOrNot(permissions.BasePermission):
    message = 'Вы не являетесь владельцем цели'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.category.user == request.user
