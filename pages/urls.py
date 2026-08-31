from django.urls import path

from quotes.views import ContactPageView, QuotePageView

from .views import (
    CmsPageView,
    HomeView,
    ProjectDetailView,
    ProjectListView,
    ServiceDetailView,
    ServiceListView,
    SolutionTopicView,
    SolutionsView,
)

app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("solutions/", SolutionsView.as_view(), name="solutions"),
    path(
        "solutions/<slug:group>/<slug:slug>/",
        SolutionTopicView.as_view(),
        name="solution_topic",
    ),
    path("cases/", ProjectListView.as_view(), name="cases"),
    path("cases/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    path("services/", ServiceListView.as_view(), name="services"),
    path("services/<slug:slug>/", ServiceDetailView.as_view(), name="service_detail"),
    path(
        "wholesale/",
        CmsPageView.as_view(
            page_slug="wholesale",
            fallback={
                "title": "Wholesale",
                "meta_description": "Wholesale partnership with Norhage Industri for distributors and professional buyers.",
                "heading": "Wholesale",
                "lead": "We supply wholesalers and distributors with industrial materials, greenhouse components, and related systems. Volume pricing is quoted per request.",
                "body": "Spec sheets, sample quantities, and project pricing are quoted per request.",
            },
        ),
        name="wholesale",
    ),
    path(
        "about/",
        CmsPageView.as_view(
            page_slug="about",
            fallback={
                "title": "About us",
                "meta_description": "Norhage Industri is the B2B brand of TEHI AS, supplying industrial materials and services across Europe.",
                "heading": "About Norhage Industri",
                "lead": "Norhage Industri is a B2B brand of TEHI AS. We supply industrial materials and professional services for commercial greenhouse, construction, and manufacturing projects.",
                "body": "Prices are quoted for each project. You can browse the catalog, select products, and ask for a quote — no customer account is required.",
            },
        ),
        name="about",
    ),
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("quote/", QuotePageView.as_view(), name="quote"),
    path(
        "terms/",
        CmsPageView.as_view(
            page_slug="terms",
            fallback={
                "title": "Terms of use",
                "meta_description": "Terms of use for the Norhage Industri website.",
                "heading": "Terms of use",
                "lead": "Legal text will be reviewed before launch.",
                "body": "",
            },
        ),
        name="terms",
    ),
    path(
        "privacy/",
        CmsPageView.as_view(
            page_slug="privacy",
            fallback={
                "title": "Privacy policy",
                "meta_description": "Privacy policy for the Norhage Industri website.",
                "heading": "Privacy policy",
                "lead": "Legal text will be reviewed before launch. Quote and contact forms will store the details you submit so sales can reply.",
                "body": "",
            },
        ),
        name="privacy",
    ),
    path(
        "cookies/",
        CmsPageView.as_view(
            page_slug="cookies",
            fallback={
                "title": "Cookie information",
                "meta_description": "Cookie information for the Norhage Industri website.",
                "heading": "Cookie information",
                "lead": "This site uses a session cookie so forms can work. Marketing cookies are not part of the MVP.",
                "body": "",
            },
        ),
        name="cookies",
    ),
]
