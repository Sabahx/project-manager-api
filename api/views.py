from django.shortcuts import render ,redirect
from rest_framework import viewsets, permissions,generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Project, Task ,Comment, TaskLog, Notification, TaskFollower, Task
from .serializers import (
    ProjectSerializer,
    TaskSerializer,
    RegisterSerializer,
    CommentSerializer,
    TaskLogSerializer,
    NotificationSerializer,
    TaskFollowerSerializer
)

from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsProjectManagerOrReadOnly, IsTaskOwnerOrProjectManager ,IsCommentAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth import authenticate, login



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated,IsProjectManagerOrReadOnly]

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

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'due_date', 'assigned_to', 'project']
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if project.manager != self.request.user:
            raise PermissionDenied("Only the project manager can create tasks.")
        serializer.save(assigned_to=self.request.user)  # Optional: auto-assign to creator

    def perform_update(self, serializer):
        task = self.get_object()
        project = task.project
        user = self.request.user

    # 🔒 الصلاحيات: فقط المكلف أو المدير يمكنه التعديل
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
                  change_type=field,
                  timestamp=timezone.now()
            )

            # إرسال إشعار للمتابعين
            followers = TaskFollower.objects.filter(task=new_instance)
            for follower in followers:
                Notification.objects.create(
                    user=follower.user,
                    message=f"Task '{new_instance.title}' was updated: {field} changed.",
                    related_task=new_instance,
                    created_at=timezone.now()
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

        # إشعارات للمتابعين
        followers = TaskFollower.objects.filter(task=task).exclude(user=self.request.user)
        for follower in followers:
            Notification.objects.create(
                user=follower.user,
                task=task,
                comment=comment,
                message=f"New comment on task '{task.title}'"
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
    
-------------------------------------------------------------------------------------------------
#HTML PAGES FUNCTIONES-BASED VIEW 
def home_view(request):
    return render(request, "home.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('project_list')  # change as needed
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        
        if password != confirm:
            return render(request, 'register.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': "Username already exists"})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('task_list')  # redirect after successful registration

    return render(request, 'register.html')
