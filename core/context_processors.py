from .menu import MAIN_NAV, MEGA_COLUMNS


def site(request):
    return {
        "company_name": "Norhage Industri",
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
    }
