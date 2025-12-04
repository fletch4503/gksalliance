from django.utils import timezone
from django.db import models

from .models import Task


def recalc_overdue():
    now = timezone.now()
    qs = Task.objects.exclude(status=Task.DONE)
    updated = qs.filter(due_date__lt=now).update(is_overdue=True)
    # передаем в updated количество просроченных задач
    Task.objects.filter(is_overdue=True).filter(
        models.Q(due_date__gte=now) | models.Q(status=Task.DONE)
    ).update(is_overdue=False)
    return updated
