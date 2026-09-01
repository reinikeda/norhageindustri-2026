from .menu import MAIN_NAV, MEGA_COLUMNS
from .seo import absolute_path, default_share_image, site_json_ld


def site(request):
    return {
        "company_name": "Norhage Industri",
        "company_legal_name": "TEHI AS",
        "company_org_number": "911 648 032",
        "company_tagline": "Greenhouses and plastic experts",
        "company_phone": "+47 940 23 135",
        "company_email": "info@norhageindustri.com",
        "company_address": "TEHI AS, Vardheivegen 68, 4340 Bryne, Norway",
        "main_nav": MAIN_NAV,
        "mega_columns": MEGA_COLUMNS,
        "social_links": [
            {
                "name": "LinkedIn",
                "url": "https://www.linkedin.com/company/norhage-industri-norge/",
                "icon": "linkedin",
            },
            {
                "name": "YouTube",
                "url": "https://www.youtube.com/@norhage_industri",
                "icon": "youtube",
            },
            {
                "name": "Facebook",
                "url": "https://www.facebook.com/people/Norhage-Industri/61551080051832/",
                "icon": "facebook",
            },
        ],
        "request_canonical": absolute_path(request),
        "default_og_image": default_share_image(request),
        "site_json_ld": site_json_ld(request),
    }

