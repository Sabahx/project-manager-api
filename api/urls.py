from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    RegisterView,
    TaskViewSet,
    CommentViewSet,
    TaskLogViewSet,
    NotificationViewSet,
    TaskFollowViewSet,
    health_check
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health-check'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logs/<int:task_id>/', TaskLogViewSet.as_view({'get': 'list'}), name='task-logs'),
    path('notifications/', NotificationViewSet.as_view({'get': 'list'}), name='notifications'),
    path('notifications/<int:pk>/mark-as-read/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='mark-as-read'),
    path('tasks/<int:pk>/follow/', TaskFollowViewSet.as_view({'post': 'follow'}), name='task-follow'),
    path('tasks/<int:pk>/unfollow/', TaskFollowViewSet.as_view({'post': 'unfollow'}), name='task-unfollow'),
]
