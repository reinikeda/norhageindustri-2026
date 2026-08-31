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
            "country",
            "location",
            "year",
            "work_type",
            "dimensions",
            "industry",
            "is_published",
            "sort_order",
        )

    def before_import_row(self, row, **kwargs):
        year = str(row.get("year") or "").strip()
        row["year"] = int(year) if year.isdigit() else None
