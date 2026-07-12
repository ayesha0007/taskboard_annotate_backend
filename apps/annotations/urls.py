from rest_framework.routers import DefaultRouter

from .views import AnnotationClassViewSet, AnnotationImageViewSet, PolygonViewSet

router = DefaultRouter()
router.register("images", AnnotationImageViewSet, basename="annotation-image")
router.register("classes", AnnotationClassViewSet, basename="annotation-class")
router.register("polygons", PolygonViewSet, basename="polygon")

urlpatterns = router.urls
