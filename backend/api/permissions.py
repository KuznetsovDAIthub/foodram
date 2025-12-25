from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для автора или администратора или чтение."""

    def has_object_permission(self, request, view, obj):
        """Проверка разрешения."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
