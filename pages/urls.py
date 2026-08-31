from django.urls import path
from django.views.generic import RedirectView

from .views import HomeView, SimplePageView, SolutionTopicView, SolutionsView

app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("solutions/", SolutionsView.as_view(), name="solutions"),
    path(
        "solutions/<slug:group>/<slug:slug>/",
        SolutionTopicView.as_view(),
        name="solution_topic",
    ),
    path(
        "products/",
        RedirectView.as_view(pattern_name="pages:solutions", permanent=False),
        name="products",
    ),
    path(
        "cases/",
        SimplePageView.as_view(
            template_name="pages/placeholder.html",
            extra_context={
                "title": "Cases & projects",
                "meta_description": "Selected industrial projects delivered with Norhage Industri materials and systems.",
                "heading": "Cases & projects",
                "lead": "Project stories will be added after the English catalog. Contact us if you need references for a similar industry or system.",
            },
        ),
        name="cases",
    ),
    path(
        "wholesale/",
        SimplePageView.as_view(
            template_name="pages/simple.html",
            extra_context={
                "title": "Wholesale",
                "meta_description": "Wholesale partnership with Norhage Industri for distributors and professional buyers.",
                "heading": "Wholesale",
                "lead": "We supply wholesalers and distributors with industrial materials, greenhouse components, and related systems. Volume pricing is quoted per request.",
                "sections": [
                    {
                        "title": "What partners can request",
                        "text": "Spec sheets, sample quantities, and project pricing for sealing tapes, vent openers, sheets, and other catalog items.",
                    },
                ],
            },
        ),
        name="wholesale",
    ),
    path(
        "services/",
        SimplePageView.as_view(
            template_name="pages/simple.html",
            extra_context={
                "title": "Services",
                "meta_description": "Industrial greenhouse assembly and repair, plus precision cutting, machining, and bending of technical plastics.",
                "heading": "Services",
                "lead": "We support commercial projects from specification through installation and maintenance.",
                "sections": [
                    {
                        "title": "Industrial greenhouse assembly and repair",
                        "text": "Custom-built systems and on-site work, from foundation through completion, including ongoing maintenance.",
                    },
                    {
                        "title": "Precision cutting, machining, and bending",
                        "text": "Technical plastics cut and formed to project drawings, with consistent quality for demanding industrial use.",
                    },
                ],
            },
        ),
        name="services",
    ),
    path(
        "about/",
        SimplePageView.as_view(
            template_name="pages/simple.html",
            extra_context={
                "title": "About us",
                "meta_description": "Norhage Industri is the B2B brand of TEHI AS, supplying industrial materials and services across Europe.",
                "heading": "About Norhage Industri",
                "lead": "Norhage Industri is a B2B brand of TEHI AS. We supply industrial materials and professional services for commercial greenhouse, construction, and manufacturing projects.",
                "sections": [
                    {
                        "title": "What we offer",
                        "text": "Commercial greenhouse systems, technical plastics, polycarbonate sheets and façades, rubber materials, profiles, fasteners, and related assembly services.",
                    },
                    {
                        "title": "How we work",
                        "text": "Prices are quoted for each project. You can browse the catalog, select products, and ask for a quote — no customer account is required.",
                    },
                ],
            },
        ),
        name="about",
    ),
    path(
        "contact/",
        SimplePageView.as_view(
            template_name="pages/contact.html",
            extra_context={
                "title": "Contact",
                "meta_description": "Contact Norhage Industri for technical advice or a project quote.",
            },
        ),
        name="contact",
    ),
    path(
        "quote/",
        SimplePageView.as_view(
            template_name="pages/placeholder.html",
            extra_context={
                "title": "Request a quote",
                "meta_description": "Ask Norhage Industri for a B2B quote. Product selection and quantities will be added with the catalog.",
                "heading": "Request a quote",
                "lead": "The quote form with product quantities will be added after the catalog. For now, use the contact page or email info@norhageindustri.com.",
            },
        ),
        name="quote",
    ),
    path(
        "terms/",
        SimplePageView.as_view(
            template_name="pages/simple.html",
            extra_context={
                "title": "Terms of use",
                "meta_description": "Terms of use for the Norhage Industri website.",
                "heading": "Terms of use",
                "lead": "Legal text will be reviewed before launch. This page exists so navigation and footer links already work.",
                "sections": [],
            },
        ),
        name="terms",
    ),
    path(
        "privacy/",
        SimplePageView.as_view(
            template_name="pages/simple.html",
            extra_context={
                "title": "Privacy policy",
                "meta_description": "Privacy policy for the Norhage Industri website.",
                "heading": "Privacy policy",
                "lead": "Legal text will be reviewed before launch. Quote and contact forms will store the details you submit so sales can reply.",
                "sections": [],
            },
        ),
        name="privacy",
    ),
    path(
        "cookies/",
        SimplePageView.as_view(
            template_name="pages/simple.html",
            extra_context={
                "title": "Cookie information",
                "meta_description": "Cookie information for the Norhage Industri website.",
                "heading": "Cookie information",
                "lead": "This site uses a session cookie so forms and the future quote basket can work. Marketing cookies are not part of the MVP.",
                "sections": [],
            },
        ),
        name="cookies",
    ),
]
