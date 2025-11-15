from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, Comment, TaskLog, Notification, TaskFollower

class UserSerializer(serializers.ModelSerializer):
    """User information serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight project serializer for list views"""
    manager = UserSerializer(read_only=True)
    task_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'manager', 'task_count', 'member_count', 'created_at']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_member_count(self, obj):
        return obj.members.count()

class ProjectSerializer(serializers.ModelSerializer):
    """Detailed project serializer"""
    manager = UserSerializer(read_only=True)
    members = UserSerializer(read_only=True, many=True)
    tasks = serializers.SerializerMethodField()
    task_stats = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'manager', 'members', 'tasks', 'task_stats', 'created_at']

    def get_tasks(self, obj):
        from .models import Task
        tasks = obj.tasks.all()[:5]  # Limit to recent 5 tasks
        return TaskListSerializer(tasks, many=True).data

    def get_task_stats(self, obj):
        tasks = obj.tasks.all()
        return {
            'total': tasks.count(),
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'done': tasks.filter(status='done').count(),
        }

class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight task serializer for list views"""
    assigned_to = UserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'due_date', 'project', 'project_name', 'assigned_to', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    """Detailed task serializer"""
    assigned_to = UserSerializer(read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    project_name = serializers.CharField(source='project.name', read_only=True)
    comment_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'due_date', 'project', 'project_name',
                  'assigned_to', 'comment_count', 'follower_count', 'is_following', 'created_at']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_follower_count(self, obj):
        return TaskFollower.objects.filter(task=obj).count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TaskFollower.objects.filter(task=obj, user=request.user).exists()
        return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
    
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_username', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']

class TaskLogSerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = TaskLog
        fields = ['id', 'task', 'field_changed', 'old_value', 'new_value', 'changed_by', 'changed_by_username', 'timestamp']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'task', 'comment', 'is_read', 'created_at']
        read_only_fields = ['user', 'message', 'task', 'comment', 'created_at']

class TaskFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFollower
        fields = ['id', 'user', 'task', 'created_at']
        read_only_fields = ['user', 'created_at']