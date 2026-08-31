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

