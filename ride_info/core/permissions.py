from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access only when the resolved user has the 'admin' role."""

    message = "Only users with the 'admin' role can access this endpoint."

    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "admin"
