from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, Task, TaskLog, Notification, TaskFollower, Comment


class SystemTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.user1.is_active = True
        self.user2.is_active = True
        self.user1.save()
        self.user2.save()

        self.project = Project.objects.create(name="Test Project", description="desc", manager=self.user1)
        self.project.members.add(self.user1, self.user2)

        self.task = Task.objects.create(
            title="Test Task",
            description="Some description",
            status="todo",
            project=self.project,
            assigned_to=self.user1
        )

    def login(self, username="user1", password="pass"):
        response = self.client.post("/api/token/", {"username": username, "password": password})
        print("Login response for", username, "➡️", response.status_code, response.data)
        assert "access" in response.data, f"JWT login failed for {username}"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data["access"])

    def test_comment_permissions(self):
        self.login("user1")
        url = "/api/comments/"
        response = self.client.post(url, {"task": self.task.id, "content": "A comment"})
        self.assertEqual(response.status_code, 201)
        comment_id = response.data["id"]

        self.login("user2")
        edit_url = f"/api/comments/{comment_id}/"
        response = self.client.patch(edit_url, {"content": "Updated"})
        self.assertEqual(response.status_code, 403)

    def test_task_log_created_on_update(self):
        self.login("user1")
        self.client.patch(f"/api/tasks/{self.task.id}/", {"status": "done"})
        self.assertTrue(TaskLog.objects.filter(task=self.task).exists())

    def test_notification_created_on_comment(self):
        TaskFollower.objects.create(user=self.user2, task=self.task)
        self.login("user1")
        self.client.post("/api/comments/", {"task": self.task.id, "content": "Test notification"})

        self.login("user2")
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_follow_unfollow_task(self):
        self.login("user1")
        follow_url = f"/api/tasks/{self.task.id}/follow/"
        unfollow_url = f"/api/tasks/{self.task.id}/unfollow/"

        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TaskFollower.objects.filter(user=self.user1, task=self.task).exists())

        response = self.client.post(unfollow_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TaskFollower.objects.filter(user=self.user1, task=self.task).exists())


class EdgeCaseTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='pass123')
        self.member = User.objects.create_user(username='member', password='pass123')
        self.other = User.objects.create_user(username='other', password='pass123')
        for user in [self.manager, self.member, self.other]:
            user.is_active = True
            user.save()

        self.project = Project.objects.create(name='Edge Project', manager=self.manager)
        self.project.members.add(self.manager, self.member)

        self.task = Task.objects.create(
            title='Edge Task',
            project=self.project,
            assigned_to=self.member,
            status='todo'
        )

    def login(self, username="user1", password="pass123"):
        response = self.client.post("/api/token/", {"username": username, "password": password})
        print("Login response for", username, "➡️", response.status_code, response.data)
        assert "access" in response.data, f"JWT login failed for {username}"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data["access"])

    def test_non_owner_cannot_update_task(self):
        self.login("other")
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.patch(url, {'status': 'done'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_duplicate_follow_prevention(self):
        self.login("member")
        url = reverse('task-follow', args=[self.task.id])
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaskFollower.objects.filter(user=self.member, task=self.task).count(), 1)

    def test_cannot_modify_notification_directly(self):
        notif = Notification.objects.create(
            user=self.member,
            task=self.task,
            message="Read-only test"
        )
        self.login("member")
        url = reverse('notifications')
        response = self.client.patch(url, {'message': 'Hack attempt'})
        self.assertEqual(response.status_code, 405)

    def test_cannot_delete_others_comment(self):
        comment = Comment.objects.create(task=self.task, author=self.manager, content="Not yours")
        self.login("member")
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_task_search_filter(self):
        self.login("member")
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
        self.assertGreaterEqual(len(response.data), 1)

    def test_multi_filter_combination(self):
        self.login("manager")
        Task.objects.create(
            title='Filtered Task',
            project=self.project,
            assigned_to=self.manager,
            status='in_progress'
        )
        url = reverse('task-list') + f'?status=in_progress&assigned_to={self.manager.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(t['status'] == 'in_progress' for t in response.data))

    def test_manager_auto_added_to_members(self):
        self.login("manager")
        url = reverse('project-list')
        response = self.client.post(url, {'name': 'AutoJoin Project'})
        self.assertEqual(response.status_code, 201)
        project_id = response.data['id']
        self.assertTrue(self.manager in Project.objects.get(id=project_id).members.all())
