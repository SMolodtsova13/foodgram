from rest_framework.permissions import (SAFE_METHODS,
                                        BasePermission,
                                        IsAuthenticatedOrReadOny)


class IsAuthorOrReadOnlyPermission(IsAuthenticatedOrReadOny):
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
        )


class IsAuthorPermission(BasePermission):
    """Проверка доступов."""

    def has_object_permission(self, request, view, obj):
        """Проверка возможностей для пользоватей с объектом."""
        return obj.author == request.user
