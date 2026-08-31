def site(request):
    return {
        "company_name": "Norhage Industri",
        "company_tagline": "Greenhouses and plastic experts",
        "company_phone": "+47 940 23 135",
        "company_email": "info@norhageindustri.com",
        "company_address": "TEHI AS, Vardheivegen 68, 4340 Bryne, Norway",
        "nav_items": [
            ("pages:home", "Home"),
            ("pages:products", "Products"),
            ("pages:services", "Services"),
            ("pages:about", "About"),
            ("pages:contact", "Contact"),
        ],
    }
