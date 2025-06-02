from rest_framework import permissions

class IsProjectManagerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.members.all()
        return obj.manager == request.user

class IsTaskOwnerOrProjectManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.project.members.all()
        return obj.assigned_to == request.user or obj.project.manager == request.user
