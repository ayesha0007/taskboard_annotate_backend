from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .models import AnnotationClass, AnnotationImage, Polygon
from .serializers import AnnotationClassSerializer, AnnotationImageSerializer, PolygonSerializer


class AnnotationImageViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            AnnotationImage.objects.filter(owner=self.request.user)
            .prefetch_related("polygons", "polygons__annotation_class")
        )

    def perform_create(self, serializer):
        image = self.request.FILES.get("image")
        serializer.save(
            owner=self.request.user,
            original_filename=getattr(image, "name", ""),
        )


class AnnotationClassViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AnnotationClass.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PolygonViewSet(viewsets.ModelViewSet):
    serializer_class = PolygonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Polygon.objects.filter(image__owner=self.request.user).select_related(
            "annotation_class"
        )
        image_id = self.request.query_params.get("image")
        if image_id:
            queryset = queryset.filter(image_id=image_id)
        return queryset

    def perform_create(self, serializer):
        image = serializer.validated_data.get("image")
        if image is None or image.owner_id != self.request.user.id:
            raise PermissionDenied("You do not own this image.")
        serializer.save()
