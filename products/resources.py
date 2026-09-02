from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import Category, Product


class CategoryResource(resources.ModelResource):
    parent = fields.Field(
        column_name="parent",
        attribute="parent",
        widget=ForeignKeyWidget(Category, field="slug"),
    )

    class Meta:
        model = Category
        import_id_fields = ("slug",)
        fields = (
            "name",
            "slug",
            "group",
            "parent",
            "description",
            "is_active",
            "sort_order",
        )


class ProductResource(resources.ModelResource):
    categories = fields.Field(
        column_name="categories",
        attribute="categories",
        widget=ManyToManyWidget(Category, field="slug", separator="|"),
    )

    class Meta:
        model = Product
        import_id_fields = ("sku",)
        fields = (
            "sku",
            "name",
            "slug",
            "short_description",
            "full_description",
            "technical_text",
            "seo_title",
            "seo_description",
            "is_active",
            "is_featured",
            "categories",
        )
        export_order = (
            "sku",
            "name",
            "slug",
            "short_description",
            "full_description",
            "technical_text",
            "seo_title",
            "seo_description",
            "is_active",
            "is_featured",
            "categories",
        )
