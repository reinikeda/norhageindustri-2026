from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        {
            "title": "Page not found",
            "meta_description": "That address is not on the Norhage Industri website.",
            "robots": "noindex, follow",
        },
        status=404,
    )


def server_error(request):
    return render(
        request,
        "500.html",
        {
            "title": "Server error",
            "meta_description": "The website could not complete that request.",
            "robots": "noindex, follow",
        },
        status=500,
    )


def robots_txt(request):
    sitemap = request.build_absolute_uri(reverse("sitemap"))
    admin_path = "/" + settings.ADMIN_URL.lstrip("/")
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Disallow: {admin_path}",
            "Disallow: /media/products/documents/",
            "",
            f"Sitemap: {sitemap}",
            "",
        ]
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
