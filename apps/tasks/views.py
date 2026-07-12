from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD for tasks. Always scoped to request.user so nobody can read or
    modify another user's board.

    GET /api/v1/tasks/?date=2026-07-07  -> tasks due on that date
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(owner=self.request.user)
        date_param = self.request.query_params.get("date")
        if date_param:
            queryset = queryset.filter(due_date=date_param)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
