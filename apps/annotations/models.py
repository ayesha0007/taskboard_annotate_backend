from django.conf import settings
from django.db import models


def annotation_image_path(instance, filename):
    return f"annotations/user_{instance.owner_id}/{filename}"


class AnnotationImage(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="annotation_images",
    )
    image = models.ImageField(upload_to=annotation_image_path)
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_filename or self.image.name


class AnnotationClass(models.Model):
    """
    A reusable label (e.g. "car", "person") a user can tag shapes with.
    Scoped per-user so two people can both have a class called "car"
    without colliding.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="annotation_classes",
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#5B8DEF")  # hex color
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="unique_class_name_per_owner")
        ]

    def __str__(self):
        return self.name


class Polygon(models.Model):
    """
    A single hand-drawn shape on an image.
    `points` is stored as a list of [x, y] pairs, normalized 0-1 relative
    to the image's width/height so annotations stay correct at any
    render size on the frontend. A "box" is simply stored as its 4
    corner points, so both shape types share the same storage format.
    """

    class ShapeType(models.TextChoices):
        POLYGON = "polygon", "Polygon"
        BOX = "box", "Box"

    image = models.ForeignKey(
        AnnotationImage,
        on_delete=models.CASCADE,
        related_name="polygons",
    )
    annotation_class = models.ForeignKey(
        AnnotationClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="polygons",
    )
    shape_type = models.CharField(max_length=10, choices=ShapeType.choices, default=ShapeType.POLYGON)
    points = models.JSONField()  # [[x1, y1], [x2, y2], ...]
    color = models.CharField(max_length=7, default="#22C55E")  # hex color
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.shape_type} #{self.pk} on image {self.image_id}"
