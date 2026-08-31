import json

from django.views.generic import DetailView

from .models import Product
from .specs import specification_notes, specification_rows


class ProductDetailView(DetailView):
    model = Product
    slug_field = "sku"
    slug_url_kwarg = "sku"
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .prefetch_related("images", "documents", "categories", "specifications")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        spec_rows = specification_rows(product)
        spec_notes = specification_notes(product)
        primary = product.primary_category()
        related = (
            Product.objects.filter(is_active=True, categories__in=product.categories.all())
            .exclude(pk=product.pk)
            .prefetch_related("images")
            .distinct()[:6]
        )
        title = product.seo_title or product.name
        description = (
            product.seo_description
            or (product.short_description[:160] if product.short_description else "")
            or product.name
        )
        canonical = self.request.build_absolute_uri(product.get_absolute_url())
        breadcrumbs = [
            {"label": "Home", "url": "/"},
            {"label": "Solutions & products", "url": "/solutions/"},
        ]
        if primary:
            breadcrumbs.append({"label": primary.name, "url": primary.get_absolute_url()})
        breadcrumbs.append({"label": product.name, "url": ""})
        images = product.image_list
        image_urls = [
            self.request.build_absolute_uri(image.file.url) for image in images if image.file
        ]
        json_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": index,
                            "name": crumb["label"],
                            "item": self.request.build_absolute_uri(crumb["url"] or product.get_absolute_url()),
                        }
                        for index, crumb in enumerate(breadcrumbs, start=1)
                    ],
                },
                {
                    "@type": "Product",
                    "@id": canonical + "#product",
                    "name": product.name,
                    "sku": product.sku,
                    "mpn": product.sku,
                    "description": description,
                    "brand": {"@type": "Brand", "name": "Norhage Industri"},
                    "url": canonical,
                    "mainEntityOfPage": {"@id": canonical + "#webpage"},
                    "category": primary.name if primary else "Industrial materials",
                    "additionalProperty": [
                        {"@type": "PropertyValue", "name": label, "value": value}
                        for label, value in spec_rows
                    ],
                    "offers": {
                        "@type": "Offer",
                        "url": canonical,
                        "availability": "https://schema.org/InStock",
                        "itemCondition": "https://schema.org/NewCondition",
                        "businessFunction": "http://purl.org/goodrelations/v1#Inquire",
                        "eligibleCustomerType": "https://schema.org/Business",
                    },
                },
            ],
        }
        if image_urls:
            json_ld["@graph"][1]["image"] = image_urls
        context.update(
            {
                "title": title,
                "meta_description": description,
                "canonical_url": canonical,
                "og_type": "product",
                "og_image": image_urls[0] if image_urls else "",
                "json_ld": json.dumps(json_ld, ensure_ascii=False),
                "breadcrumbs": breadcrumbs,
                "spec_rows": spec_rows,
                "spec_notes": spec_notes,
                "related_products": related,
                "primary_category": primary,
            }
        )
        return context
