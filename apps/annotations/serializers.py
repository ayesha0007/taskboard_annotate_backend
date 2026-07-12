from django.conf import settings
from rest_framework import serializers

from .models import AnnotationClass, AnnotationImage, Polygon

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class AnnotationClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationClass
        fields = ["id", "name", "color", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Class name cannot be empty.")
        if len(value) > 100:
            raise serializers.ValidationError("Class name must be 100 characters or fewer.")
        return value

    def validate_color(self, value):
        if not value.startswith("#") or len(value) not in (4, 7):
            raise serializers.ValidationError("Color must be a hex code like #22C55E.")
        return value


class PolygonSerializer(serializers.ModelSerializer):
    annotation_class_detail = AnnotationClassSerializer(source="annotation_class", read_only=True)

    class Meta:
        model = Polygon
        fields = [
            "id",
            "image",
            "annotation_class",
            "annotation_class_detail",
            "shape_type",
            "points",
            "color",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_points(self, value):
        if not isinstance(value, list) or len(value) < 3:
            raise serializers.ValidationError("A shape needs at least 3 points.")
        for point in value:
            if (
                not isinstance(point, (list, tuple))
                or len(point) != 2
                or not all(isinstance(coord, (int, float)) for coord in point)
            ):
                raise serializers.ValidationError("Each point must be a [x, y] pair of numbers.")
            x, y = point
            if not (0 <= x <= 1 and 0 <= y <= 1):
                raise serializers.ValidationError("Point coordinates must be normalized between 0 and 1.")
        return value

    def validate_color(self, value):
        if not value.startswith("#") or len(value) not in (4, 7):
            raise serializers.ValidationError("Color must be a hex code like #22C55E.")
        return value

    def validate_annotation_class(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request and value.owner_id != request.user.id:
            raise serializers.ValidationError("You do not own this class.")
        return value


class AnnotationImageSerializer(serializers.ModelSerializer):
    polygons = PolygonSerializer(many=True, read_only=True)

    class Meta:
        model = AnnotationImage
        fields = ["id", "image", "original_filename", "uploaded_at", "polygons"]
        read_only_fields = ["id", "uploaded_at", "polygons"]

    def validate_image(self, value):
        max_size_bytes = settings.MAX_UPLOAD_IMAGE_SIZE_MB * 1024 * 1024
        if value.size > max_size_bytes:
            raise serializers.ValidationError(
                f"Image must be smaller than {settings.MAX_UPLOAD_IMAGE_SIZE_MB}MB."
            )
        content_type = getattr(value, "content_type", None)
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")
        return value
