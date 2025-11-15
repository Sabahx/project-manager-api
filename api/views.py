from rest_framework import viewsets, permissions, generics, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db import connection
from .models import Project, Task, Comment, TaskLog, Notification, TaskFollower
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    TaskSerializer,
    TaskListSerializer,
    RegisterSerializer,
    CommentSerializer,
    TaskLogSerializer,
    NotificationSerializer,
    TaskFollowerSerializer
)

from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProjectManagerOrReadOnly, IsTaskOwnerOrProjectManager, IsCommentAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connection
        connection.ensure_connection()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'

    return Response({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'database': db_status,
        'api': 'operational'
    })


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectManagerOrReadOnly]

    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        # Automatically set the current user as manager
        project = serializer.save(manager=self.request.user)
        project.members.add(self.request.user)  # Add manager as a member too

    def get_queryset(self):
        # Show only projects where the user is a member
        return Project.objects.filter(members=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskOwnerOrProjectManager]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'due_date', 'assigned_to', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'status']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        """Show only tasks from projects where user is a member"""
        return Task.objects.filter(project__members=self.request.user)

    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def get_serializer_context(self):
        """Pass request to serializer for is_following field"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if project.manager != self.request.user:
            raise PermissionDenied("Only the project manager can create tasks.")
        serializer.save(assigned_to=self.request.user)  # Optional: auto-assign to creator

    def perform_update(self, serializer):
        task = self.get_object()
        project = task.project
        user = self.request.user

        # Permission check: only assignee or manager can update
        if user != task.assigned_to and user != project.manager:
            raise permissions.PermissionDenied("You do not have permission to update this task.")

        old_values = {field: getattr(task, field) for field in ['status', 'description', 'assigned_to']}
        new_instance = serializer.save()
        new_values = {field: getattr(new_instance, field) for field in ['status', 'description', 'assigned_to']}

        for field in old_values:
            if old_values[field] != new_values[field]:
                TaskLog.objects.create(
                    task=new_instance,
                    changed_by=user,
                    field_changed=field,
                    old_value=str(old_values[field]),
                    new_value=str(new_values[field])
                )

                # Send notifications to followers
                followers = TaskFollower.objects.filter(task=new_instance).exclude(user=user)
                for follower in followers:
                    Notification.objects.create(
                        user=follower.user,
                        message=f"Task '{new_instance.title}' was updated: {field} changed.",
                        task=new_instance
                    )

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(task__project__members=self.request.user)

    def perform_create(self, serializer):
        task = serializer.validated_data['task']
        if self.request.user not in task.project.members.all():
            raise PermissionDenied("Only project members can comment.")

        comment = serializer.save(author=self.request.user)

        # Send notifications to task followers
        followers = TaskFollower.objects.filter(task=task).exclude(user=self.request.user)
        for follower in followers:
            Notification.objects.create(
                user=follower.user,
                task=task,
                comment=comment,
                message=f"New comment on task '{task.title}' by {self.request.user.username}"
            )

class TaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        task = Task.objects.get(id=task_id)
        if self.request.user not in task.project.members.all():
            raise PermissionDenied("You are not a member of this task's project.")
        return TaskLog.objects.filter(task=task)

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'detail': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class TaskFollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        task = Task.objects.get(pk=pk)
        TaskFollower.objects.get_or_create(user=request.user, task=task)
        return Response({'detail': 'Now following task.'})

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        TaskFollower.objects.filter(user=request.user, task__id=pk).delete()
        return Response({'detail': 'Unfollowed task.'})