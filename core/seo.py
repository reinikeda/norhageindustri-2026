import json

from django.templatetags.static import static


def absolute_path(request, path=None):
    return request.build_absolute_uri(path or request.path)


def default_share_image(request):
    return absolute_path(request, static("img/logo-on-dark.png"))


def organization_id(request):
    return absolute_path(request, "/") + "#organization"


def website_id(request):
    return absolute_path(request, "/") + "#website"


def site_graph(request):
    origin = absolute_path(request, "/")
    org_id = organization_id(request)
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["Organization", "LocalBusiness"],
                "@id": org_id,
                "name": "Norhage Industri",
                "legalName": "TEHI AS",
                "identifier": "911 648 032",
                "url": origin,
                "email": "info@norhageindustri.com",
                "telephone": "+47 940 23 135",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Vardheivegen 68",
                    "postalCode": "4340",
                    "addressLocality": "Bryne",
                    "addressCountry": "NO",
                },
                "logo": default_share_image(request),
                "sameAs": [
                    "https://www.linkedin.com/company/norhage-industri-norge/",
                    "https://www.youtube.com/@norhage_industri",
                    "https://www.facebook.com/people/Norhage-Industri/61551080051832/",
                ],
            },
            {
                "@type": "WebSite",
                "@id": website_id(request),
                "url": origin,
                "name": "Norhage Industri",
                "inLanguage": "en-GB",
                "publisher": {"@id": org_id},
            },
            {
                "@type": "WebPage",
                "@id": absolute_path(request) + "#webpage",
                "url": absolute_path(request),
                "isPartOf": {"@id": website_id(request)},
                "about": {"@id": org_id},
                "inLanguage": "en-GB",
            },
        ],
    }


def site_json_ld(request):
    return json.dumps(site_graph(request), ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")
