from django.test import TestCase, override_settings
from django.urls import reverse

from core.menu import find_topic


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
        response = self.client.get(reverse("pages:products"))
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


class MenuTests(TestCase):
    def test_find_topic(self):
        topic = find_topic("industry", "food-manufacturing")
        self.assertEqual(topic["label"], "Food Manufacturing")
        self.assertIsNone(find_topic("industry", "missing"))
