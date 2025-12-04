from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users (2 admins, 3 users)"

    def handle(self, *args, **options):
        users = []
        # Create 2 admins
        for i in range(1, 3):
            username = f"admin{i}"
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("123852")
                user.is_staff = True
                user.is_superuser = True
                user.save()
            users.append(user)

        # Create 3 normal users
        for i in range(1, 4):
            username = f"user{i}"
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("123852")
                user.save()
            users.append(user)

        self.stdout.write(
            self.style.SUCCESS(
                "Created test users: %s" % ",".join([u.username for u in users])
            )
        )
