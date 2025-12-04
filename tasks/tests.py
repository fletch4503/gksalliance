from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Task
import json
from django.utils import timezone
from datetime import timedelta
import logging as log

User = get_user_model()
log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TaskAPITest(TestCase):
    """Минимальный набор автотестов Task Manager API"""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="testuser1")
        self.user2 = User.objects.create(username="testuser2")
        log.info("Starting test: %s", self._testMethodName)

    def _headers(self, user):
        """Helper to create X-User-Id headers for Django test client"""
        return {"X-User-Id": str(user.id)}

    # ============================================================================
    # REQUIREMENT 1: Тест успешного создания задачи
    # ============================================================================
    def test_create_task_success(self):
        """
        - Задача должна содержать заголовок (title)
        - Задача присваивается только аутентифицированному пользователю (owner)
        - Ответ статусом 201 Created
        """
        data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "status": "todo",
        }
        resp = self.client.post(
            "/api/tasks/",
            data=json.dumps(data),
            content_type="application/json",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        body = json.loads(resp.content)
        self.assertEqual(body["title"], "Buy groceries")
        self.assertEqual(body["owner"], self.user1.id)
        self.assertEqual(body["status"], "todo")
        log.info("Test %s completed", self._testMethodName)

    # ============================================================================
    # REQUIREMENT 2: Тест нарушения бизнес-правила (например, нельзя установить status="done" без due_date)
    # ============================================================================
    def test_status_done_requires_due_date(self):
        """
        - Должен возвращать статус 400 - Bad Request
        - Должен включать валидацию ошибок в ответе
        """
        data = {
            "title": "Finish project",
            "status": "done",
            # Пропущен due_date - это нарушение бизнес-правила
        }
        resp = self.client.post(
            "/api/tasks/",
            data=json.dumps(data),
            content_type="application/json",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = json.loads(resp.content)
        self.assertIn("due_date", body)  # Ошибка должна упоминать due_date

    def test_status_done_with_due_date_succeeds(self):
        """
        Тест, который устанавливает status='done' с due_date.
        - Должен возвращать статус 201 - Created
        """
        now = timezone.now()
        data = {
            "title": "Complete task",
            "status": "done",
            "due_date": (now + timedelta(days=1)).isoformat(),
        }
        resp = self.client.post(
            "/api/tasks/",
            data=json.dumps(data),
            content_type="application/json",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        body = json.loads(resp.content)
        self.assertEqual(body["status"], "done")

    # ============================================================================
    # REQUIREMENT 3: тест на проверку доступа (нельзя удалить чужую задачу)
    # ============================================================================
    def test_cannot_delete_others_task(self):
        """
        - User1 создает задачу
        - User2 пытается ее удалить
        - Должен вернуться статус 403 Forbidden или 404 Not Found
        """
        # User2 creates a task
        task = Task.objects.create(title="User2's task", owner=self.user2)

        # User1 tries to delete it
        resp = self.client.delete(
            f"/api/tasks/{task.id}/",
            headers=self._headers(self.user1),
        )
        # Should be denied (403 or 404 - either is acceptable)
        self.assertIn(
            resp.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_can_delete_own_task(self):
        """
        Тест, при котором пользователь МОЖЕТ удалить свою задачу.
        - User1 создает задачу
        - User1 удаляет ее
        - Должен вернуться статус 204 No Content
        """
        task = Task.objects.create(title="User1's task", owner=self.user1)

        resp = self.client.delete(
            f"/api/tasks/{task.id}/",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # Verify task is actually deleted
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    # ============================================================================
    # BONUS TESTS: Фильтрация, пагинация и права доступа
    # ============================================================================
    def test_cannot_view_others_task(self):
        """
        Тест, при котором пользователь не может видеть задачи другого пользователя.
        """
        task = Task.objects.create(title="User2's task", owner=self.user2)

        resp = self.client.get(
            f"/api/tasks/{task.id}/",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_only_own_tasks(self):
        """
        Тест, при котором возвращается список задач только текущего пользователя.
        """
        # Create tasks for both users
        Task.objects.create(title="User1 Task 1", owner=self.user1)
        Task.objects.create(title="User1 Task 2", owner=self.user1)
        Task.objects.create(title="User2 Task 1", owner=self.user2)

        # List tasks as User1
        resp = self.client.get(
            "/api/tasks/",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        body = json.loads(resp.content)

        # Should see only User1's tasks
        self.assertEqual(body["count"], 2)
        for task in body["results"]:
            self.assertEqual(task["owner"], self.user1.id)

    def test_filter_by_status(self):
        """
        Фильтрация задач по статусу.
        """
        Task.objects.create(title="Todo 1", owner=self.user1, status="todo")
        Task.objects.create(title="Todo 2", owner=self.user1, status="todo")
        Task.objects.create(
            title="Done 1",
            owner=self.user1,
            status="done",
            due_date=timezone.now(),
        )

        resp = self.client.get(
            "/api/tasks/?status=todo",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        body = json.loads(resp.content)

        self.assertEqual(body["count"], 2)
        for task in body["results"]:
            self.assertEqual(task["status"], "todo")

    def test_pagination_works(self):
        """
        Пагинация работает только при заданном параметре size.
        """
        # Create 5 tasks
        for i in range(5):
            Task.objects.create(title=f"Task {i}", owner=self.user1)

        # Request with size=2
        resp = self.client.get(
            "/api/tasks/?size=2",
            headers=self._headers(self.user1),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        body = json.loads(resp.content)

        self.assertEqual(len(body["results"]), 2)
        self.assertEqual(body["count"], 5)
