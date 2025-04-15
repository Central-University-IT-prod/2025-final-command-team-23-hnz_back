from rest_framework.permissions import BasePermission


class IsUserCompany(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return

        return hasattr(request.user, 'company') and request.user.company is not None

    def has_object_permission(self, request, view, obj):
        return obj.company == request.user.company
