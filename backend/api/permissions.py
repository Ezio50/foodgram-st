from rest_framework import permissions


class UserSelfPermission(permissions.BasePermission):

    # Only checks auth for /users/me/ endpoint
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.pk == request.user
        )


class OwnershipPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
