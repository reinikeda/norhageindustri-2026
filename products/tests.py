from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from tablib import Dataset

from products.models import Category, Product
from products.resources import ProductResource


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.material = Category.objects.create(
            name="Polycarbonate",
            slug="polycarbonate",
            group=Category.Group.MATERIAL,
        )
        self.industry = Category.objects.create(
            name="Building & Architecture",
            slug="building-architecture",
            group=Category.Group.INDUSTRY,
        )
        self.product = Product.objects.create(
            sku="PC-MW-16",
            name="16 mm multiwall polycarbonate sheet",
            short_description="Multiwall sheet for roofs and façades.",
            is_active=True,
        )
        self.product.categories.set([self.material, self.industry])

    def test_product_can_belong_to_several_subcategories(self):
        self.assertEqual(self.product.categories.count(), 2)
        self.assertIn(self.product, self.material.products.all())
        self.assertIn(self.product, self.industry.products.all())

    def test_product_appears_on_each_category_page(self):
        for group, slug in (
            ("material", "polycarbonate"),
            ("industry", "building-architecture"),
        ):
            url = reverse("pages:solution_topic", kwargs={"group": group, "slug": slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, self.product.name)
            self.assertContains(response, self.product.sku)

    def test_published_product_detail(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, "Polycarbonate")

    def test_unpublished_product_is_404(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse("products:detail", kwargs={"sku": self.product.sku}))
        self.assertEqual(response.status_code, 404)


class ProductCsvImportTests(TestCase):
    def setUp(self):
        Category.objects.create(name="Polycarbonate", slug="polycarbonate", group="material")
        Category.objects.create(
            name="Food Manufacturing",
            slug="food-manufacturing",
            group="industry",
        )

    def test_csv_import_assigns_categories_by_slug(self):
        dataset = Dataset()
        dataset.headers = [
            "sku",
            "name",
            "slug",
            "short_description",
            "full_description",
            "technical_text",
            "seo_title",
            "seo_description",
            "is_active",
            "is_featured",
            "categories",
        ]
        dataset.append(
            [
                "PC-SOLID-4",
                "4 mm solid polycarbonate sheet",
                "4mm-solid-polycarbonate-sheet",
                "Solid sheet for guards.",
                "Quoted per size.",
                "4 mm",
                "",
                "",
                "1",
                "0",
                "polycarbonate|food-manufacturing",
            ]
        )
        result = ProductResource().import_data(dataset, dry_run=False)
        self.assertFalse(result.has_errors(), result.row_errors())
        product = Product.objects.get(sku="PC-SOLID-4")
        slugs = set(product.categories.values_list("slug", flat=True))
        self.assertEqual(slugs, {"polycarbonate", "food-manufacturing"})


class SeedCatalogTests(TestCase):
    def test_seed_creates_menu_categories_and_demo_product(self):
        call_command("seed_catalog", "--demo")
        self.assertTrue(Category.objects.filter(slug="polycarbonate").exists())
        product = Product.objects.get(sku="PC-MW-16")
        self.assertGreaterEqual(product.categories.count(), 2)
        call_command("seed_catalog", "--demo")
        self.assertEqual(Product.objects.filter(sku="PC-MW-16").count(), 1)


class ExampleCatalogCsvTests(TestCase):
    def test_live_site_example_csv_imports(self):
        call_command("seed_catalog")
        path = settings.BASE_DIR / "docs" / "examples" / "products.csv"
        dataset = Dataset().load(path.read_text(encoding="utf-8"), format="csv")
        result = ProductResource().import_data(dataset, dry_run=False)
        self.assertFalse(result.has_errors(), result.row_errors())
        self.assertGreaterEqual(Product.objects.count(), 140)
        makan = Product.objects.get(sku="GH-GREENHOUSE-MAKAN")
        self.assertTrue(makan.categories.filter(slug="food-manufacturing").exists())
        self.assertTrue(makan.categories.filter(slug="turnkey-facilities").exists())
        sheets = Product.objects.get(sku="PL-MULTIWALL-POLYCARBONATE-ROOFING-GLAZING-SHEETS")
        self.assertTrue(sheets.categories.filter(slug="polycarbonate").exists())
