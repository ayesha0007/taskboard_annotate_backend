from django.contrib import admin

from .models import AnnotationClass, AnnotationImage, Polygon


class PolygonInline(admin.TabularInline):
    model = Polygon
    extra = 0


@admin.register(AnnotationImage)
class AnnotationImageAdmin(admin.ModelAdmin):
    list_display = ["id", "owner", "original_filename", "uploaded_at"]
    inlines = [PolygonInline]


@admin.register(AnnotationClass)
class AnnotationClassAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "color", "created_at"]
    search_fields = ["name"]
