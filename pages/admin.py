from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Page, Project, ProjectImage, Service
from .resources import PageResource, ProjectResource, ServiceResource


@admin.register(Page)
class PageAdmin(ImportExportModelAdmin):
    resource_classes = [PageResource]
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "heading", "lead")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("slug", "title", "heading", "lead", "body", "image")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
        ("Publishing", {"fields": ("is_published", "created_at", "updated_at")}),
    )


@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):
    resource_classes = [ServiceResource]
    list_display = ("name", "slug", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("name", "summary")
    prepopulated_fields = {"slug": ("name",)}


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    resource_classes = [ProjectResource]
    list_display = ("title", "country", "year", "work_type", "is_published", "sort_order")
    list_filter = ("is_published", "work_type", "country", "year")
    search_fields = ("title", "summary", "country", "location", "industry")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "body", "image")}),
        (
            "Facts",
            {
                "fields": (
                    "work_type",
                    "country",
                    "location",
                    "year",
                    "dimensions",
                    "industry",
                )
            },
        ),
        ("Publishing", {"fields": ("is_published", "sort_order")}),
    )
