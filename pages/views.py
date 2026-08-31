from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView

from core.menu import find_topic
from products.models import Category, Product

from .models import Page, Project, Service


def published_page(slug):
    return Page.objects.filter(slug=slug, is_published=True).first()


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("home")
        context["page"] = page
        if page:
            context["title"] = page.seo_title or page.title
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


class ContactPageView(CmsPageView):
    template_name = "pages/contact.html"
    page_slug = "contact"
    fallback = {
        "title": "Contact",
        "meta_description": "Contact Norhage Industri for technical advice or a project quote.",
        "heading": "Contact",
        "lead": "Use these details for technical questions or a project discussion.",
        "body": "",
    }


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
        lead = ""
        if category and category.description:
            lead = category.description
        elif topic:
            lead = (
                f"{topic['group_title']}. The product list for this topic will be added with the "
                "English catalog. Ask for a quote and we will match materials, systems, and quantities."
            )
        products = []
        if category:
            products = category.products.filter(is_active=True).prefetch_related("images")
        context.update(
            {
                "title": heading,
                "meta_description": f"{heading} solutions from Norhage Industri.",
                "heading": heading,
                "lead": lead,
                "category": category,
                "products": products,
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

    def get_queryset(self):
        return Project.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("cases")
        context["page"] = page
        context["title"] = page.title if page else "Cases & projects"
        context["heading"] = page.heading if page else "Cases & projects"
        context["lead"] = (
            page.lead
            if page
            else "Selected industrial projects delivered with Norhage Industri materials and systems."
        )
        context["meta_description"] = context["lead"][:160]
        return context


class ProjectDetailView(DetailView):
    template_name = "pages/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        context["meta_description"] = self.object.summary[:160]
        return context
