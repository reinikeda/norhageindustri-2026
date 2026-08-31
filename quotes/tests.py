from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from products.models import Product
from quotes.models import Inquiry


class InquiryFormTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.product = Product.objects.create(
            sku="PC-MW-16",
            name="16 mm multiwall polycarbonate sheet",
            is_active=True,
        )

    def contact_payload(self, **overrides):
        data = {
            "name": "Ada Buyer",
            "company": "Acme Greenhouses",
            "email": "ada@acme.test",
            "phone": "+47 940 23 135",
            "message": "Can you machine a sample panel?",
            "website": "",
        }
        data.update(overrides)
        return data

    def quote_payload(self, **overrides):
        data = {
            "name": "Ada Buyer",
            "company": "Acme Greenhouses",
            "email": "ada@acme.test",
            "phone": "+47 940 23 135",
            "country": "Norway",
            "message": "Roof package for a food plant.",
            "website": "",
            "lines-TOTAL_FORMS": "3",
            "lines-INITIAL_FORMS": "0",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "8",
            "lines-0-product": str(self.product.pk),
            "lines-0-quantity": "12",
            "lines-1-product": "",
            "lines-1-quantity": "",
            "lines-2-product": "",
            "lines-2-quantity": "",
        }
        data.update(overrides)
        return data

    def test_contact_page_shows_form_not_only_details(self):
        response = self.client.get(reverse("pages:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Work email")
        self.assertContains(response, "Send a message")
        self.assertContains(response, reverse("pages:quote"))

    def test_quote_page_shows_product_lines(self):
        response = self.client.get(reverse("pages:quote"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delivery country")
        self.assertContains(response, "Products and quantities")
        self.assertContains(response, "Send quote request")

    def test_quote_page_prefills_sku_from_query(self):
        response = self.client.get(f"{reverse('pages:quote')}?sku={self.product.sku}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.sku)
        self.assertContains(response, f'value="{self.product.pk}"')

    def test_contact_submit_stores_inquiry_and_sends_mail(self):
        response = self.client.post(reverse("pages:contact"), self.contact_payload())
        self.assertRedirects(
            response,
            f"{reverse('quotes:thanks')}?kind=contact",
            fetch_redirect_response=False,
        )
        inquiry = Inquiry.objects.get()
        self.assertEqual(inquiry.kind, Inquiry.Kind.CONTACT)
        self.assertEqual(inquiry.company, "Acme Greenhouses")
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("Acme Greenhouses", mail.outbox[0].subject)
        thanks = self.client.get(response["Location"])
        self.assertContains(thanks, "Request received")
        self.assertContains(thanks, "noindex")

    def test_quote_submit_stores_lines(self):
        response = self.client.post(reverse("pages:quote"), self.quote_payload())
        self.assertRedirects(
            response,
            f"{reverse('quotes:thanks')}?kind=quote",
            fetch_redirect_response=False,
        )
        inquiry = Inquiry.objects.get()
        self.assertEqual(inquiry.kind, Inquiry.Kind.QUOTE)
        self.assertEqual(inquiry.country, "Norway")
        line = inquiry.lines.get()
        self.assertEqual(line.sku, "PC-MW-16")
        self.assertEqual(line.quantity, 12)
        self.assertEqual(line.product_name, self.product.name)
        self.assertEqual(len(mail.outbox), 2)

    def test_quote_requires_a_product_line(self):
        response = self.client.post(
            reverse("pages:quote"),
            self.quote_payload(**{"lines-0-product": "", "lines-0-quantity": ""}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Inquiry.objects.exists())
        self.assertContains(response, "Add at least one product and quantity.")

    def test_quote_rejects_quantity_without_product(self):
        response = self.client.post(
            reverse("pages:quote"),
            self.quote_payload(**{"lines-0-product": "", "lines-0-quantity": "4"}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Inquiry.objects.exists())

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            reverse("pages:contact"),
            self.contact_payload(email="not-an-email"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Inquiry.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_is_rejected(self):
        response = self.client.post(
            reverse("pages:contact"),
            self.contact_payload(website="https://spam.example"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Inquiry.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_inquiry_is_kept_when_email_fails(self):
        with patch("quotes.views.notify_inquiry", side_effect=RuntimeError("smtp down")):
            response = self.client.post(reverse("pages:contact"), self.contact_payload())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Inquiry.objects.filter(email="ada@acme.test").exists())

    def test_rate_limit_after_six_successful_submits(self):
        for index in range(6):
            payload = self.contact_payload(email=f"ada{index}@acme.test")
            response = self.client.post(reverse("pages:contact"), payload)
            self.assertEqual(response.status_code, 302)
        blocked = self.client.post(reverse("pages:contact"), self.contact_payload())
        self.assertEqual(blocked.status_code, 200)
        self.assertContains(blocked, "Please wait before sending another request.")
        self.assertEqual(Inquiry.objects.count(), 6)
