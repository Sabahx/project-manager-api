from rest_framework import viewsets, permissions,generics, filters
from rest_framework.decorators import action
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer ,RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsProjectManagerOrReadOnly, IsTaskOwnerOrProjectManager
from django_filters.rest_framework import DjangoFilterBackend


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
            raise permissions.PermissionDenied("Only the project manager can create tasks.")
        serializer.save(assigned_to=self.request.user)  # Optional: auto-assign to creator

    def get_queryset(self):
        return Task.objects.filter(project__members=self.request.user)
