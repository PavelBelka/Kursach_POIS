from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerProfileOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user

class IsReaderOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS and request.user.is_staff == False) or request.user.is_staff == True:
            return True
        else:
            return False