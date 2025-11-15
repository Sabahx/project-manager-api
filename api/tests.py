from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Project, Task, TaskFollower, Notification, Comment

class EdgeCaseTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='pass123')
        self.member = User.objects.create_user(username='member', password='pass123')
        self.other = User.objects.create_user(username='other', password='pass123')

        self.project = Project.objects.create(name='Edge Project', manager=self.manager)
        self.project.members.add(self.manager, self.member)

        self.task = Task.objects.create(
            title='Edge Task',
            project=self.project,
            assigned_to=self.member,
            status='todo'
        )

        self.login_url = reverse('token_obtain_pair')

    def login(self, user):
        res = self.client.post(self.login_url, {'username': user.username, 'password': 'pass123'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + res.data['access'])

    def test_non_owner_cannot_update_task(self):
        self.login(self.other)
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.patch(url, {'status': 'done'}, format='json')
        # 404 because task is not in their project queryset (which is correct - they shouldn't even see it)
        self.assertEqual(response.status_code, 404)

    def test_duplicate_follow_prevention(self):
        self.login(self.member)
        url = reverse('task-follow', args=[self.task.id])
        self.client.post(url)
        response = self.client.post(url)  # try follow again
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaskFollower.objects.filter(user=self.member, task=self.task).count(), 1)

    def test_cannot_modify_notification_directly(self):
        notif = Notification.objects.create(
            user=self.member,
            task=self.task,
            message="Read-only test"
        )
        self.login(self.member)
        url = reverse('notifications')
        response = self.client.patch(url, {'message': 'Hack attempt'})
        self.assertEqual(response.status_code, 405)  # PATCH not allowed on list view

    def test_cannot_delete_others_comment(self):
        comment = Comment.objects.create(task=self.task, author=self.manager, content="Not yours")
        self.login(self.member)
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_task_search_filter(self):
        self.login(self.member)
        Task.objects.create(
            title='Meeting notes',
            description='discuss project',
            project=self.project,
            assigned_to=self.member,
            status='todo'
        )
        url = reverse('task-list') + '?search=meeting'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Handle paginated response
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)

    def test_multi_filter_combination(self):
        self.login(self.manager)
        Task.objects.create(
            title='Filtered Task',
            project=self.project,
            assigned_to=self.manager,
            status='in_progress'
        )
        url = reverse('task-list') + '?status=in_progress&assigned_to={}'.format(self.manager.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Handle paginated response
        results = response.data.get('results', response.data)
        self.assertTrue(all(t['status'] == 'in_progress' for t in results))

    def test_manager_auto_added_to_members(self):
        self.login(self.manager)
        url = reverse('project-list')
        response = self.client.post(url, {'name': 'AutoJoin Project'})
        self.assertEqual(response.status_code, 201)
        project_id = response.data['id']
        self.assertTrue(
            self.manager in Project.objects.get(id=project_id).members.all()
        )