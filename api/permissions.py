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

class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.task.project.members.all()
        return obj.author == request.user

class IsProjectMember(permissions.BasePermission):
    """Used for generic access where being in the project is required."""
    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id') or view.kwargs.get('pk')
        if not task_id:
            return False
        from .models import Task
        try:
            task = Task.objects.get(pk=task_id)
            return request.user in task.project.members.all()
        except Task.DoesNotExist:
            return False