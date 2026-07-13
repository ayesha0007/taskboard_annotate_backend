from django.conf import settings
from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(db_index=True)
    due_time = models.TimeField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)  # e.g. ["frontend", "urgent"]

    # rich-text content written in the per-task document editor
    content = models.TextField(blank=True, default="")
    # base64 PNG data URL for the freehand sketch layer
    sketch_data = models.TextField(blank=True, default="")

    # order within its column, used for drag-and-drop persistence
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "position"]
        indexes = [models.Index(fields=["owner", "due_date"])]

    def __str__(self):
        return f"{self.title} ({self.status})"
