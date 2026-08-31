from import_export import resources

from .models import Page, Project, Service


class PageResource(resources.ModelResource):
    class Meta:
        model = Page
        import_id_fields = ("slug",)
        fields = (
            "slug",
            "title",
            "heading",
            "lead",
            "body",
            "seo_title",
            "seo_description",
            "is_published",
        )


class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service
        import_id_fields = ("slug",)
        fields = (
            "name",
            "slug",
            "summary",
            "body",
            "is_published",
            "sort_order",
        )


class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project
        import_id_fields = ("slug",)
        fields = (
            "title",
            "slug",
            "summary",
            "body",
            "industry",
            "is_published",
            "sort_order",
        )
