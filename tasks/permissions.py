from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            getattr(request.user, "is_authenticated", False)
            and obj.owner_id == request.user.id
        )
