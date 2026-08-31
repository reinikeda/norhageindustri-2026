from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from pages.models import Page, Project, Service
from products.models import Product


class PagesTests(TestCase):
    def test_home_renders(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Norhage Industri")
        self.assertContains(response, "Ask for a quote")
        self.assertContains(response, "logo-on-dark.png")
        self.assertContains(response, "Solutions &amp; Products")
        self.assertContains(response, "By industry")
        self.assertContains(response, "Polycarbonate")
        self.assertContains(response, "Turnkey Facilities")
        self.assertContains(response, "linkedin.com/company/norhage-industri-norge")
        self.assertContains(response, "youtube.com/@norhage_industri")
        self.assertContains(response, "facebook.com/people/Norhage-Industri")

    def test_key_pages_render(self):
        names = [
            "pages:solutions",
            "pages:cases",
            "pages:wholesale",
            "pages:services",
            "pages:about",
            "pages:contact",
            "pages:quote",
            "pages:terms",
            "pages:privacy",
            "pages:cookies",
        ]
        for name in names:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_old_products_url_redirects_to_solutions(self):
        response = self.client.get(reverse("products:index"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("pages:solutions"))

    def test_solution_topic_page(self):
        url = reverse(
            "pages:solution_topic",
            kwargs={"group": "material", "slug": "polycarbonate"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Polycarbonate")

    def test_unknown_solution_topic_is_404(self):
        url = reverse(
            "pages:solution_topic",
            kwargs={"group": "material", "slug": "does-not-exist"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_admin_login_is_reachable(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_unknown_url_uses_custom_404(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(response, "noindex", status_code=404)

    def test_robots_and_sitemap_are_published(self):
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "Sitemap:")
        self.assertContains(robots, "Disallow: /admin/")
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, reverse("pages:home"))
        self.assertContains(sitemap, reverse("pages:solutions"))
        self.assertContains(sitemap, reverse("pages:quote"))

    def test_contact_and_quote_pages_have_forms(self):
        contact = self.client.get(reverse("pages:contact"))
        quote = self.client.get(reverse("pages:quote"))
        self.assertContains(contact, "Work email")
        self.assertContains(quote, "Delivery country")

    def test_home_has_canonical_and_organization_schema(self):
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, '"@type": ["Organization", "LocalBusiness"]')
        self.assertContains(response, "twitter:card")
        self.assertNotContains(response, ">Home |")


class CmsPageTests(TestCase):
    def test_about_uses_published_cms_page(self):
        Page.objects.create(
            slug="about",
            title="About TEHI",
            heading="About TEHI AS",
            lead="Edited in admin.",
            body="Body copy from admin.",
            is_published=True,
        )
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About TEHI AS")
        self.assertContains(response, "Edited in admin.")
        self.assertContains(response, "Body copy from admin.")

    def test_unpublished_cms_page_uses_fallback_copy(self):
        Page.objects.create(
            slug="about",
            title="Hidden",
            heading="Hidden heading",
            lead="Should not appear.",
            is_published=False,
        )
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Norhage Industri")
        self.assertNotContains(response, "Hidden heading")

    def test_unpublished_service_and_project_are_404(self):
        service = Service.objects.create(
            name="Hidden service",
            slug="hidden-service",
            is_published=False,
        )
        project = Project.objects.create(
            title="Hidden project",
            slug="hidden-project",
            is_published=False,
        )
        self.assertEqual(self.client.get(service.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)

    def test_published_service_and_project_render(self):
        service = Service.objects.create(
            name="Greenhouse assembly",
            slug="greenhouse-assembly",
            summary="On-site installation.",
            is_published=True,
        )
        project = Project.objects.create(
            title="Food greenhouse",
            slug="food-greenhouse",
            summary="Cladding package.",
            industry="Food manufacturing",
            is_published=True,
        )
        self.assertContains(self.client.get(reverse("pages:services")), service.name)
        self.assertContains(self.client.get(service.get_absolute_url()), service.summary)
        self.assertContains(self.client.get(reverse("pages:cases")), project.title)
        self.assertContains(self.client.get(project.get_absolute_url()), project.summary)

    def test_seed_updates_old_quote_placeholder_copy(self):
        Page.objects.create(
            slug="quote",
            title="Request a quote",
            heading="Request a quote",
            lead="The quote form with product quantities will be added after the catalog. For now, email us.",
            is_published=True,
        )
        call_command("seed_catalog", verbosity=0)
        page = Page.objects.get(slug="quote")
        self.assertNotIn("will be added after the catalog", page.lead)
        self.assertIn("quantities, and destination", page.lead)

    def test_home_shows_featured_products(self):
        product = Product.objects.create(
            sku="FEAT-1",
            name="Featured demo product",
            short_description="Shown on the homepage.",
            is_active=True,
            is_featured=True,
        )
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, product.name)
        self.assertNotContains(response, "Commercial greenhouses")


class ProjectCaseTests(TestCase):
    def setUp(self):
        self.norway = Project.objects.create(
            title="Stavanger roof renovation",
            slug="stavanger-roof-renovation",
            summary="Channel polycarbonate roof replacement.",
            body="Old channel polycarbonate was removed and a new roof was installed.",
            country="Norway",
            location="Stavanger",
            year=2024,
            work_type=Project.WorkType.RENOVATION,
            dimensions="Quoted on site",
            is_published=True,
        )
        self.sweden = Project.objects.create(
            title="Mellanå greenhouse assembly",
            slug="mellana-greenhouse-assembly",
            summary="New industrial greenhouse hall.",
            country="Sweden",
            year=2026,
            work_type=Project.WorkType.ASSEMBLY,
            dimensions="25 × 90 m (2,250 m²)",
            is_published=True,
        )

    def test_list_shows_facts_and_filters(self):
        response = self.client.get(reverse("pages:cases"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.norway.title)
        self.assertContains(response, "Norway")
        self.assertContains(response, "2024")
        self.assertContains(response, "Renovation")
        self.assertContains(response, "2 published projects")
        self.assertContains(response, 'name="type"')
        self.assertContains(response, 'rel="canonical"')

    def test_filter_by_country_and_type(self):
        norway = self.client.get(reverse("pages:cases"), {"country": "Norway"})
        self.assertContains(norway, self.norway.title)
        self.assertNotContains(norway, self.sweden.title)
        self.assertContains(norway, "noindex")
        renovation = self.client.get(reverse("pages:cases"), {"type": "renovation"})
        self.assertContains(renovation, self.norway.title)
        self.assertNotContains(renovation, self.sweden.title)

    def test_detail_shows_fact_table(self):
        response = self.client.get(self.norway.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stavanger")
        self.assertContains(response, "What was done")
        self.assertContains(response, "Related projects")
        self.assertContains(response, self.sweden.title)


class ExamplePagesCsvTests(TestCase):
    def test_live_site_pages_csv_imports(self):
        call_command("import_pages_csv")
        slugs = {
            "home",
            "solutions",
            "about",
            "wholesale",
            "contact",
            "quote",
            "services",
            "cases",
            "terms",
            "privacy",
            "cookies",
        }
        self.assertEqual(set(Page.objects.values_list("slug", flat=True)), slugs)
        about = Page.objects.get(slug="about")
        self.assertIn("TEHI AS", about.lead)
        terms = Page.objects.get(slug="terms")
        self.assertIn("Norwegian law", terms.body)
        privacy = Page.objects.get(slug="privacy")
        self.assertIn("personal data", privacy.lead.lower())
        response = self.client.get(reverse("pages:about"))
        self.assertContains(response, "Our Story")


class ExampleProjectsCsvTests(TestCase):
    def test_live_site_projects_csv_imports(self):
        call_command("import_projects_csv")
        self.assertEqual(Project.objects.count(), 10)
        fire = Project.objects.get(slug="fire-damaged-industrial-greenhouse-renovation")
        self.assertEqual(fire.country, "Sweden")
        self.assertEqual(fire.work_type, Project.WorkType.RENOVATION)
        self.assertIn("640 m²", fire.dimensions)
        assembly = self.client.get(reverse("pages:cases"), {"type": "assembly"})
        self.assertContains(assembly, "Reo industrial greenhouse")
        self.assertNotContains(assembly, fire.title)

