from rest_framework import permissions

class IsStaffOrAbove(permissions.BasePermission):
    """
    Allows access only to staff, supervisor, owner, or superuser roles.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ["staff", "supervisor", "owner", "superuser"]
        )
