from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnlyPermission(BasePermission):
    """Проверка доступов."""

    def has_permission(self, request, view):
        """Проверка возможностей для пользоватей."""
        return (
            (request.method in SAFE_METHODS or request.method == 'POST')
            or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        """Проверка возможностей для пользоватей с объектом."""
        return (
            (request.method in SAFE_METHODS or request.method == 'POST')
            or obj.author == request.user
            or request.user.is_admin
            )
