from django.test import TestCase, override_settings
from django.urls import reverse


class PagesTests(TestCase):
    def test_home_renders(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Norhage Industri")
        self.assertContains(response, "Ask for a quote")
        self.assertContains(response, "logo-on-dark.png")

    def test_key_pages_render(self):
        names = [
            "pages:products",
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

    def test_admin_login_is_reachable(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_unknown_url_uses_custom_404(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
