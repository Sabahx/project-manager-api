from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Project, Task

class ProjectTaskTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='pass123')
        self.member = User.objects.create_user(username='member', password='pass123')
        self.other_user = User.objects.create_user(username='outsider', password='pass123')

        self.project = Project.objects.create(name='Test Project', manager=self.manager)
        self.project.members.add(self.manager, self.member)

        self.task = Task.objects.create(
            title='Initial Task',
            project=self.project,
            assigned_to=self.member,
            status='todo'
        )

        self.login_url = reverse('token_obtain_pair')

    def authenticate(self, user):
        response = self.client.post(self.login_url, {'username': user.username, 'password': 'pass123'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

    def test_project_visibility(self):
        self.authenticate(self.member)
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_project_edit(self):
        self.authenticate(self.member)
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.patch(url, {'name': 'Hacked Project'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_task_creation_by_manager(self):
        self.authenticate(self.manager)
        url = reverse('task-list')
        response = self.client.post(url, {
            'title': 'New Task',
            'project': self.project.id,
            'assigned_to': self.member.id,
            'status': 'todo'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_tasks_by_status(self):
        self.authenticate(self.manager)
        url = reverse('task-list') + '?status=todo'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_search_tasks_by_title(self):
        self.authenticate(self.manager)
        url = reverse('task-list') + '?search=Initial'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
