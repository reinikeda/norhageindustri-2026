from django.http import Http404
from django.views.generic import TemplateView

from core.menu import find_topic


class HomeView(TemplateView):
    template_name = "pages/home.html"


class SimplePageView(TemplateView):
    extra_context = {}


class SolutionsView(TemplateView):
    template_name = "pages/solutions.html"
    extra_context = {
        "title": "Solutions & products",
        "meta_description": "Browse Norhage Industri solutions by industry, material, and system.",
    }


class SolutionTopicView(TemplateView):
    template_name = "pages/placeholder.html"

    def get_context_data(self, **kwargs):
        topic = find_topic(kwargs["group"], kwargs["slug"])
        if topic is None:
            raise Http404("Unknown solution topic")
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": topic["label"],
                "meta_description": f"{topic['label']} solutions from Norhage Industri.",
                "heading": topic["label"],
                "lead": (
                    f"{topic['group_title']}. The product list for this topic will be added with the "
                    "English catalog. Ask for a quote and we will match materials, systems, and quantities."
                ),
            }
        )
        return context
