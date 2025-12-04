from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner
from .services import recalc_overdue
from .filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not (user and getattr(user, "is_authenticated", False)):
            return Task.objects.none()
        # возвращает только задачи, принадлежащие текущему аутентифицированному пользователю
        qs = Task.objects.filter(owner=user).order_by("-created_at")
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Пользователь должен быть аутентифицирован для операций GET-list и POST-create.
        # Для остальных требуется, чтобы пользователь был owner-ом задачи
        if self.action in ["list", "create"]:
            return [IsAuthenticated()]
        return [IsOwner()]


@api_view(["POST"])
@permission_classes([IsAdminUser])
def recalc_overdue_view(request):
    updated = recalc_overdue()
    return Response({"updated": updated}, status=status.HTTP_200_OK)
