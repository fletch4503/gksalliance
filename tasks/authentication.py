from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class XUserIdAuthentication(BaseAuthentication):
    """
    Аутентификация по заголовку X-User-Id.

    Алгоритм:
    1. Клиент отправляет X-User-Id в заголовке
    2. Предполагаем, что такой пользователь есть в базе
    3. Если заголовок не получен или пользователь не найден, возвращаем AnonymousUser

    Пример использования через CURL:
        curl -H "X-User-Id: 1" http://localhost:8000/api/tasks/
    """

    def authenticate(self, request):
        # Пытаемся получить X-User-Id из заголовков
        user_id = request.headers.get("X-User-Id") or request.META.get("HTTP_X_USER_ID")

        if not user_id:
            return (AnonymousUser(), None)

        try:
            # Переводим в int and проверяем пользователя
            user = User.objects.get(pk=int(user_id))
            return (user, None)
        except (User.DoesNotExist, ValueError):
            # Пользователь не найден или invalid ID format, возвращаем anonymous
            return (AnonymousUser(), None)
