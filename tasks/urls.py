from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, recalc_overdue_view

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("tasks/recalculate_overdue/", recalc_overdue_view, name="recalculate-overdue"),
    path("", include(router.urls)),
]
