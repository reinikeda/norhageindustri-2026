from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Category, Product, ProductDocument, ProductImage, ProductSpecification
from .resources import CategoryResource, ProductResource


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_classes = [CategoryResource]
    list_display = ("name", "group", "parent", "is_active", "sort_order")
    list_filter = ("group", "is_active", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 4


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    list_display = ("name", "sku", "is_active", "is_featured", "updated_at")
    list_filter = ("is_active", "is_featured", "categories")
    search_fields = ("name", "sku", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("categories",)
    inlines = [ProductImageInline, ProductSpecificationInline, ProductDocumentInline]
    fieldsets = (
        (None, {"fields": ("sku", "name", "slug", "categories")}),
        ("Content", {"fields": ("short_description", "full_description", "technical_text")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
        ("Publishing", {"fields": ("is_active", "is_featured")}),
    )
