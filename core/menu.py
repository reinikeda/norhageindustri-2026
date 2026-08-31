"""Main navigation and Solutions & Products mega menu.

The menu is defined in code, not in Django admin. When the catalog exists,
these topic URLs can point at real category pages without changing the header
layout.
"""

MAIN_NAV = [
    {"label": "Home", "url_name": "pages:home"},
    {
        "label": "Solutions & Products",
        "url_name": "pages:solutions",
        "mega": True,
    },
    {"label": "Cases & Projects", "url_name": "pages:cases"},
    {"label": "Wholesale", "url_name": "pages:wholesale"},
    {"label": "About us", "url_name": "pages:about"},
    {"label": "Contact", "url_name": "pages:contact"},
]

MEGA_COLUMNS = [
    {
        "title": "By industry",
        "group": "industry",
        "topics": [
            ("food-manufacturing", "Food Manufacturing"),
            ("signage-advertisement", "Signage & Advertisement"),
            ("building-architecture", "Building & Architecture"),
            ("offshore-maritime", "Offshore & Maritime"),
            ("logistics-warehousing", "Logistics & Warehousing"),
        ],
    },
    {
        "title": "By material",
        "group": "material",
        "topics": [
            ("polycarbonate", "Polycarbonate"),
            ("pmma-signage-plastics", "PMMA & Signage Plastics"),
            ("technical-plastics", "Technical Plastics"),
            ("food-grade-plastics", "Food-Grade Plastics"),
            ("industrial-rubbers-mats", "Industrial Rubbers & Mats"),
            ("metals-aluminum-copper-stainless-steel", "Metals: Aluminum, Copper & Stainless Steel"),
            ("safety-glass", "Safety Glass"),
            ("technical-fabrics", "Technical Fabrics"),
        ],
    },
    {
        "title": "By system",
        "group": "system",
        "topics": [
            ("turnkey-facilities", "Turnkey Facilities"),
            ("facade-glazing-systems", "Facade & Glazing Systems"),
            ("environmental-control-automation", "Environmental Control & Automation Systems"),
            ("industrial-curtain-door-systems", "Industrial Curtain & Door Systems"),
            ("precision-fabrication-custom-cnc", "Precision Fabrication & Custom CNC"),
            ("retrofit-spares-upgrades", "Retrofit, Spares & Upgrades"),
        ],
    },
]


def find_topic(group, slug):
    for column in MEGA_COLUMNS:
        if column["group"] != group:
            continue
        for item_slug, label in column["topics"]:
            if item_slug == slug:
                return {
                    "group": group,
                    "group_title": column["title"],
                    "slug": slug,
                    "label": label,
                }
    return None
