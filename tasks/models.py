from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

    STATUS_CHOICES = [
        (TODO, "To do"),
        (IN_PROGRESS, "In progress"),
        (DONE, "Done"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    due_date = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_overdue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.owner})"
