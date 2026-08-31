from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

from core.local_schema import catalog_schema_is_current, rebuild_sqlite_catalog_tables
from core.menu import MEGA_COLUMNS
from pages.models import Page, Project, Service
from products.models import Category, Product, ProductSpecification


PAGE_DEFAULTS = [
    {
        "slug": "home",
        "title": "Home",
        "heading": "Industrial greenhouse systems, technical plastics, and façade materials.",
        "lead": (
            "We supply commercial projects across Europe. Browse by industry, material, "
            "or system, then ask for a quote — prices are not published on the website."
        ),
        "body": "",
        "seo_title": "",
        "seo_description": "B2B supplier of industrial greenhouse systems, technical plastics, and façade materials.",
    },
    {
        "slug": "solutions",
        "title": "Solutions & products",
        "heading": "Solutions & products",
        "lead": (
            "Browse by industry, material, or system. Each topic lists published products. "
            "Ask for a quote — prices are not shown on the website."
        ),
        "body": "",
        "seo_title": "",
        "seo_description": "Browse Norhage Industri solutions by industry, material, and system.",
    },
    {
        "slug": "about",
        "title": "About us",
        "heading": "About Norhage Industri",
        "lead": (
            "Norhage Industri is a B2B brand of TEHI AS. We supply industrial materials "
            "and professional services for commercial greenhouse, construction, and manufacturing projects."
        ),
        "body": (
            "Prices are quoted for each project. You can browse the catalog, select products, "
            "and ask for a quote — no customer account is required."
        ),
        "seo_title": "",
        "seo_description": "Norhage Industri is the B2B brand of TEHI AS, supplying industrial materials and services across Europe.",
    },
    {
        "slug": "wholesale",
        "title": "Wholesale",
        "heading": "Wholesale",
        "lead": (
            "We supply wholesalers and distributors with industrial materials, greenhouse "
            "components, and related systems. Volume pricing is quoted per request."
        ),
        "body": "Spec sheets, sample quantities, and project pricing are quoted per request.",
        "seo_title": "",
        "seo_description": "Wholesale partnership with Norhage Industri for distributors and professional buyers.",
    },
    {
        "slug": "contact",
        "title": "Contact",
        "heading": "Contact",
        "lead": "Use these details for technical questions or a project discussion.",
        "body": "",
        "seo_title": "",
        "seo_description": "Contact Norhage Industri for technical advice or a project quote.",
    },
    {
        "slug": "quote",
        "title": "Request a quote",
        "heading": "Request a quote",
        "lead": (
            "Tell us the products, quantities, and destination. Sales replies with a "
            "project quote — prices are not published on the website."
        ),
        "body": "",
        "seo_title": "",
        "seo_description": "Ask Norhage Industri for a B2B quote. Include products, quantities, and destination.",
    },
    {
        "slug": "services",
        "title": "Services",
        "heading": "Services",
        "lead": "We support commercial projects from specification through installation and maintenance.",
        "body": "",
        "seo_title": "",
        "seo_description": "Industrial greenhouse assembly and repair, plus precision cutting, machining, and bending of technical plastics.",
    },
    {
        "slug": "cases",
        "title": "Cases & projects",
        "heading": "Cases & projects",
        "lead": "Selected industrial projects delivered with Norhage Industri materials and systems.",
        "body": "",
        "seo_title": "",
        "seo_description": "Selected industrial projects delivered with Norhage Industri materials and systems.",
    },
    {
        "slug": "terms",
        "title": "Terms of use",
        "heading": "Terms of use",
        "lead": "Legal text will be reviewed before launch.",
        "body": "",
        "seo_title": "",
        "seo_description": "Terms of use for the Norhage Industri website.",
    },
    {
        "slug": "privacy",
        "title": "Privacy policy",
        "heading": "Privacy policy",
        "lead": "Legal text will be reviewed before launch. Quote and contact forms will store the details you submit so sales can reply.",
        "body": "",
        "seo_title": "",
        "seo_description": "Privacy policy for the Norhage Industri website.",
    },
    {
        "slug": "cookies",
        "title": "Cookie information",
        "heading": "Cookie information",
        "lead": "This site uses a session cookie so forms can work. Marketing cookies are not part of the MVP.",
        "body": "",
        "seo_title": "",
        "seo_description": "Cookie information for the Norhage Industri website.",
    },
]


class Command(BaseCommand):
    help = "Create menu categories, starter CMS pages, and optional demo catalog items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Also create sample products, services, and a project.",
        )

    def handle(self, *args, **options):
        self.ensure_catalog_schema()
        created_categories = self.seed_categories()
        created_pages = self.seed_pages()
        extra = {"products": 0, "services": 0, "projects": 0}
        if options["demo"]:
            extra = self.seed_demo()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded "
                f"{created_categories} categories, {created_pages} pages"
                + (
                    f", {extra['products']} products, {extra['services']} services, "
                    f"{extra['projects']} projects"
                    if options["demo"]
                    else ""
                )
                + "."
            )
        )

    def ensure_catalog_schema(self):
        try:
            call_command("migrate", interactive=False, verbosity=0)
        except (OperationalError, ProgrammingError) as exc:
            if connection.vendor != "sqlite":
                raise CommandError(
                    "The database is missing catalog tables or columns. "
                    "Run python manage.py migrate."
                ) from exc
            self.stdout.write(
                self.style.WARNING(
                    "Local database tables are from an older schema. "
                    "Rebuilding pages, products, and quotes tables (admin users are kept)."
                )
            )
            rebuild_sqlite_catalog_tables()
        if catalog_schema_is_current():
            return
        if connection.vendor != "sqlite":
            raise CommandError(
                "The database is missing catalog columns (for example pages_page.created_at). "
                "Run python manage.py migrate."
            )
        self.stdout.write(
            self.style.WARNING(
                "Local database tables are from an older schema. "
                "Rebuilding pages, products, and quotes tables (admin users are kept)."
            )
        )
        rebuild_sqlite_catalog_tables()
        if not catalog_schema_is_current():
            raise CommandError(
                "Catalog tables are still missing columns. Stop the server, delete db.sqlite3, "
                "then run: python manage.py migrate && python manage.py createsuperuser && "
                "python manage.py seed_catalog --demo"
            )

    def seed_categories(self):
        created = 0
        sort = 0
        for column in MEGA_COLUMNS:
            for slug, label in column["topics"]:
                sort += 10
                _, was_created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": label,
                        "group": column["group"],
                        "description": f"{column['title']}: {label}.",
                        "sort_order": sort,
                    },
                )
                if was_created:
                    created += 1
        return created

    def seed_pages(self):
        created = 0
        for data in PAGE_DEFAULTS:
            page, was_created = Page.objects.get_or_create(slug=data["slug"], defaults=data)
            if was_created:
                created += 1
                continue
            lead = page.lead or ""
            if "will be added after the catalog" in lead or "future quote basket" in lead:
                page.lead = data["lead"]
                page.seo_description = data["seo_description"]
                page.body = data.get("body", "")
                page.save(update_fields=["lead", "seo_description", "body"])
        return created

    def seed_demo(self):
        services = [
            {
                "name": "Greenhouse assembly and repair",
                "slug": "greenhouse-assembly-and-repair",
                "summary": "On-site work from installation through maintenance for commercial greenhouse projects.",
                "body": "We plan installation, coordinate deliveries, and return for repair and spare parts.",
                "sort_order": 10,
            },
            {
                "name": "Precision plastics work",
                "slug": "precision-plastics-work",
                "summary": "Cutting, machining, and bending of technical plastics to project specifications.",
                "body": "Send drawings or a sample. We quote machining, cutting, and forming for project quantities.",
                "sort_order": 20,
            },
        ]
        services_created = 0
        for data in services:
            _, was_created = Service.objects.get_or_create(slug=data["slug"], defaults=data)
            if was_created:
                services_created += 1

        project, project_created = Project.objects.get_or_create(
            slug="commercial-greenhouse-envelope",
            defaults={
                "title": "Commercial greenhouse envelope",
                "summary": "Polycarbonate cladding, profiles, and sealing supplied for a food-production greenhouse.",
                "body": "Materials were specified with the contractor and quoted as a project package. No public prices.",
                "country": "Norway",
                "location": "Rogaland",
                "year": 2024,
                "work_type": Project.WorkType.ASSEMBLY,
                "dimensions": "Quoted per project",
                "industry": "Food manufacturing",
                "sort_order": 10,
            },
        )

        product, product_created = Product.objects.get_or_create(
            sku="PC-MW-16",
            defaults={
                "name": "16 mm multiwall polycarbonate sheet",
                "slug": "16mm-multiwall-polycarbonate-sheet",
                "short_description": "Multiwall polycarbonate for greenhouse roofs and industrial façades.",
                "full_description": (
                    "Quoted per project for sheet size, UV side, and quantity. "
                    "Matching profiles and tapes can be added to the same inquiry."
                ),
                "technical_text": "Typical thickness: 16 mm. UV protection on the outer face. Exact values confirmed on the quote.",
                "is_active": True,
                "is_featured": True,
            },
        )
        if product_created:
            product.categories.set(
                Category.objects.filter(slug__in=["polycarbonate", "building-architecture"])
            )
        if not product.specifications.exists():
            ProductSpecification.objects.bulk_create(
                [
                    ProductSpecification(product=product, label="Thickness", value="16 mm", sort_order=10),
                    ProductSpecification(product=product, label="Structure", value="Multiwall", sort_order=20),
                    ProductSpecification(product=product, label="UV protection", value="Outer face", sort_order=30),
                    ProductSpecification(product=product, label="Use", value="Greenhouse roofs and industrial façades", sort_order=40),
                ]
            )

        return {
            "products": 1 if product_created else 0,
            "services": services_created,
            "projects": 1 if project_created else 0,
        }
