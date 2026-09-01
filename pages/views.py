import json

from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView

from core.menu import find_topic
from products.models import Category, Product

from .models import Page, Project, Service, WholesaleCatalog


def published_page(slug):
    return Page.objects.filter(slug=slug, is_published=True).first()


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("home")
        context["page"] = page
        if page:
            if page.seo_title:
                context["title"] = page.seo_title
            elif page.title and page.title.lower() != "home":
                context["title"] = page.title
            context["meta_description"] = page.seo_description or page.lead[:160]
            context["home_heading"] = page.heading
            context["home_lead"] = page.lead
        context["featured_products"] = (
            Product.objects.filter(is_active=True, is_featured=True)
            .prefetch_related("images")[:8]
        )
        context["published_services"] = Service.objects.filter(is_published=True)[:4]
        return context


class CmsPageView(TemplateView):
    template_name = "pages/cms_page.html"
    page_slug = ""
    fallback = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page(self.page_slug)
        context["page"] = page
        if page:
            context.update(
                {
                    "title": page.seo_title or page.title,
                    "meta_description": page.seo_description or page.lead[:160],
                    "heading": page.heading,
                    "lead": page.lead,
                    "body": page.body,
                }
            )
        else:
            context.update(self.fallback)
        return context


class AboutPageView(CmsPageView):
    template_name = "pages/about.html"
    page_slug = "about"
    fallback = {
        "title": "About us",
        "meta_description": "Norhage Industri is the B2B brand of TEHI AS, supplying industrial materials and services across Europe.",
        "heading": "About Norhage Industri",
        "lead": (
            "Norhage Industri is a B2B brand of TEHI AS. We supply industrial materials "
            "and professional services for commercial greenhouse, construction, and manufacturing projects."
        ),
        "body": (
            "There is no public showroom. Materials and assembly are quoted per project and "
            "delivered to the site. Prices are not published on the website."
        ),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        heading = context.get("heading") or "About Norhage Industri"
        context["breadcrumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": heading, "url": ""},
        ]
        context["recent_projects"] = list(
            Project.objects.filter(is_published=True).prefetch_related("images")[:3]
        )
        return context


class WholesalePageView(CmsPageView):
    template_name = "pages/wholesale.html"
    page_slug = "wholesale"
    fallback = {
        "title": "Wholesale",
        "meta_description": "Wholesale partnership with Norhage Industri for distributors and professional buyers.",
        "heading": "Wholesale partnership",
        "lead": (
            "We supply wholesalers and distributors with industrial materials, greenhouse "
            "components, and related systems. Volume pricing is quoted per request."
        ),
        "body": (
            "Download a catalog PDF for specifications. Volume prices, branding, and "
            "minimum quantities are confirmed on a quote — they are not published on the website."
        ),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["catalogs"] = WholesaleCatalog.objects.filter(is_published=True)
        heading = context.get("heading") or "Wholesale partnership"
        context["breadcrumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": heading, "url": ""},
        ]
        return context


class SolutionsView(TemplateView):
    template_name = "pages/solutions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("solutions")
        context["page"] = page
        context["title"] = page.seo_title or page.title if page else "Solutions & products"
        context["meta_description"] = (
            page.seo_description
            if page and page.seo_description
            else "Browse Norhage Industri solutions by industry, material, and system."
        )
        context["heading"] = page.heading if page else "Solutions & products"
        context["lead"] = (
            page.lead
            if page
            else (
                "Browse by industry, material, or system. Each topic lists published "
                "products. Ask for a quote — prices are not shown on the website."
            )
        )
        return context


class SolutionTopicView(TemplateView):
    template_name = "pages/topic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = kwargs["group"]
        slug = kwargs["slug"]
        category = Category.objects.filter(group=group, slug=slug, is_active=True).first()
        topic = find_topic(group, slug)
        if category is None and topic is None:
            raise Http404("Unknown solution topic")
        heading = category.name if category else topic["label"]
        group_title = category.get_group_display() if category else topic["group_title"]
        products = []
        if category:
            products = list(
                category.products.filter(is_active=True).prefetch_related("images").order_by("name")
            )
        if category and category.description and len(category.description) > 80:
            lead = category.description
        else:
            lead = (
                f"{heading} products from Norhage Industri for commercial projects. "
                "Browse specifications and documents, then ask for a quote — prices are not published."
            )
        sibling_categories = []
        if category:
            sibling_categories = (
                Category.objects.filter(group=category.group, is_active=True)
                .exclude(pk=category.pk)[:8]
            )
        canonical = self.request.build_absolute_uri(self.request.path)
        breadcrumbs = [
            {"label": "Home", "url": "/"},
            {"label": "Solutions & products", "url": "/solutions/"},
            {"label": heading, "url": ""},
        ]
        item_list = [
            {
                "@type": "ListItem",
                "position": index,
                "url": self.request.build_absolute_uri(item.get_absolute_url()),
                "name": item.name,
            }
            for index, item in enumerate(products[:20], start=1)
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
                            "item": self.request.build_absolute_uri(crumb["url"] or self.request.path),
                        }
                        for index, crumb in enumerate(breadcrumbs, start=1)
                    ],
                },
                {
                    "@type": "CollectionPage",
                    "@id": canonical + "#webpage",
                    "name": heading,
                    "description": lead[:160],
                    "url": canonical,
                    "mainEntity": {
                        "@type": "ItemList",
                        "numberOfItems": len(products),
                        "itemListElement": item_list,
                    },
                },
            ],
        }
        context.update(
            {
                "title": heading,
                "meta_description": lead[:160],
                "canonical_url": canonical,
                "og_type": "website",
                "json_ld": json.dumps(json_ld, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e"),
                "heading": heading,
                "lead": lead,
                "group_title": group_title,
                "category": category,
                "products": products,
                "product_count": len(products),
                "sibling_categories": sibling_categories,
                "breadcrumbs": breadcrumbs,
            }
        )
        return context


class ServiceListView(ListView):
    template_name = "pages/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("services")
        context["page"] = page
        context["title"] = page.title if page else "Services"
        context["heading"] = page.heading if page else "Services"
        context["lead"] = page.lead if page else "We support commercial projects from specification through installation and maintenance."
        context["meta_description"] = (
            page.seo_description
            if page and page.seo_description
            else "Industrial greenhouse assembly and repair, plus precision cutting, machining, and bending of technical plastics."
        )
        return context


class ServiceDetailView(DetailView):
    template_name = "pages/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.name
        context["meta_description"] = self.object.summary[:160]
        return context


class ProjectListView(ListView):
    template_name = "pages/project_list.html"
    context_object_name = "projects"

    def selected_filters(self):
        work_type = self.request.GET.get("type", "").strip()
        if work_type not in Project.WorkType.values:
            work_type = ""
        year_raw = self.request.GET.get("year", "").strip()
        year = year_raw if year_raw.isdigit() else ""
        country = self.request.GET.get("country", "").strip()
        return {"type": work_type, "year": year, "country": country}

    def get_queryset(self):
        queryset = Project.objects.filter(is_published=True)
        selected = self.selected_filters()
        if selected["type"]:
            queryset = queryset.filter(work_type=selected["type"])
        if selected["year"]:
            queryset = queryset.filter(year=int(selected["year"]))
        if selected["country"]:
            queryset = queryset.filter(country__iexact=selected["country"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("cases")
        selected = self.selected_filters()
        published = Project.objects.filter(is_published=True)
        countries = list(
            published.exclude(country="").order_by("country").values_list("country", flat=True).distinct()
        )
        years = list(
            published.exclude(year=None).order_by("-year").values_list("year", flat=True).distinct()
        )
        used_types = set(published.exclude(work_type="").values_list("work_type", flat=True))
        work_types = [
            (value, label) for value, label in Project.WorkType.choices if value in used_types
        ]
        heading = page.heading if page else "Cases & projects"
        lead = (
            page.lead
            if page
            else "Selected industrial projects delivered with Norhage Industri materials and systems."
        )
        is_filtered = any(selected.values())
        canonical = self.request.build_absolute_uri("/cases/")
        breadcrumbs = [
            {"label": "Home", "url": "/"},
            {"label": heading, "url": ""},
        ]
        item_list = [
            {
                "@type": "ListItem",
                "position": index,
                "url": self.request.build_absolute_uri(item.get_absolute_url()),
                "name": item.title,
            }
            for index, item in enumerate(context["projects"][:20], start=1)
        ]
        json_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Home",
                            "item": self.request.build_absolute_uri("/"),
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": heading,
                            "item": canonical,
                        },
                    ],
                },
                {
                    "@type": "CollectionPage",
                    "@id": canonical + "#webpage",
                    "name": heading,
                    "description": lead[:160],
                    "url": canonical,
                    "mainEntity": {
                        "@type": "ItemList",
                        "numberOfItems": len(context["projects"]),
                        "itemListElement": item_list,
                    },
                },
            ],
        }
        context.update(
            {
                "page": page,
                "title": page.seo_title or page.title if page else "Cases & projects",
                "heading": heading,
                "lead": lead,
                "meta_description": (page.seo_description if page and page.seo_description else lead[:160]),
                "canonical_url": canonical,
                "robots": "noindex, follow" if is_filtered else "index, follow",
                "json_ld": json.dumps(json_ld, ensure_ascii=False)
                .replace("<", "\\u003c")
                .replace(">", "\\u003e"),
                "breadcrumbs": breadcrumbs,
                "selected": selected,
                "filter_countries": countries,
                "filter_years": years,
                "filter_types": work_types,
                "is_filtered": is_filtered,
                "result_count": len(context["projects"]),
            }
        )
        return context


class ProjectDetailView(DetailView):
    template_name = "pages/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related("images")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        related = list(
            Project.objects.filter(is_published=True, work_type=project.work_type)
            .exclude(pk=project.pk)
            .prefetch_related("images")[:3]
        ) if project.work_type else []
        if len(related) < 3:
            extra = (
                Project.objects.filter(is_published=True)
                .exclude(pk=project.pk)
                .exclude(pk__in=[item.pk for item in related])
                .prefetch_related("images")[: 3 - len(related)]
            )
            related.extend(extra)
        canonical = self.request.build_absolute_uri(project.get_absolute_url())
        description = (project.summary or project.title)[:160]
        breadcrumbs = [
            {"label": "Home", "url": "/"},
            {"label": "Cases & projects", "url": "/cases/"},
            {"label": project.title, "url": ""},
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
                            "item": self.request.build_absolute_uri(crumb["url"] or project.get_absolute_url()),
                        }
                        for index, crumb in enumerate(breadcrumbs, start=1)
                    ],
                },
                {
                    "@type": "CreativeWork",
                    "name": project.title,
                    "description": description,
                    "url": canonical,
                    "inLanguage": "en-GB",
                },
            ],
        }
        context.update(
            {
                "title": project.title,
                "meta_description": description,
                "canonical_url": canonical,
                "json_ld": json.dumps(json_ld, ensure_ascii=False)
                .replace("<", "\\u003c")
                .replace(">", "\\u003e"),
                "breadcrumbs": breadcrumbs,
                "related_projects": related,
            }
        )
        return context
