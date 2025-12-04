import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    # Если переданы параметры в URL, например, ?status=pending
    status = django_filters.CharFilter(field_name="status")
    due_date_from = django_filters.DateTimeFilter(
        field_name="due_date", lookup_expr="gte"
    )
    due_date_to = django_filters.DateTimeFilter(
        field_name="due_date", lookup_expr="lte"
    )

    class Meta:
        model = Task
        fields = ["status", "due_date_from", "due_date_to"]
