from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnlyPermission(BasePermission):
    """Проверка доступов."""

    def has_permission(self, request, view):
        """Проверка возможностей для пользоватей."""
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверка возможностей для пользоватей с объектом."""
        print("has_object_permission")
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            # or request.user.is_admin
            # or request.user.is_staff
        )


class IsAuthorPermission(BasePermission):
    """Проверка доступов."""

    def has_object_permission(self, request, view, obj):
        """Проверка возможностей для пользоватей с объектом."""
        return obj.author == request.user
