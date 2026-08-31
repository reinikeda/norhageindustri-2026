from django.views.generic import DetailView

from .models import Product


class ProductDetailView(DetailView):
    model = Product
    slug_field = "sku"
    slug_url_kwarg = "sku"
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .prefetch_related("images", "documents", "categories")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.seo_title or self.object.name
        context["meta_description"] = (
            self.object.seo_description
            or self.object.short_description[:160]
            or self.object.name
        )
        return context
