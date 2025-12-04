from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "due_date",
            "owner",
            "created_at",
            "updated_at",
            "is_overdue",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_overdue", "owner"]

    def validate(self, data):
        # Когда статус установлен в "done", due_date должен присутствовать в запрашиваемых данных
        if data.get("status") == Task.DONE and not data.get("due_date"):
            raise serializers.ValidationError(
                {"due_date": 'due_date должен быть задан, если статус="done".'}
            )
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["owner"] = request.user
        return super().create(validated_data)
