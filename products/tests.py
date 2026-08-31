from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from tablib import Dataset

from products.models import Category, Product, ProductDocument, ProductImage, ProductSpecification
from products.resources import ProductResource
from products.specs import parse_specification_text


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


class SpecParserTests(TestCase):
    def test_imported_bullet_line_becomes_table_rows(self):
        text = (
            "- Multiwall polycarbonate structure – Superior thermal insulation "
            "- UV-protected surface – Long-lasting clarity "
            "- Exterior glazing and cladding"
        )
        rows, notes = parse_specification_text(text)
        self.assertEqual(
            rows[0],
            ("Multiwall polycarbonate structure", "Superior thermal insulation"),
        )
        self.assertIn("Exterior glazing", notes)

    def test_markdown_table(self):
        text = "| Property | Value |\n| --- | --- |\n| Width | 4 m |\n| Height | 2.5 m |"
        rows, notes = parse_specification_text(text)
        self.assertEqual(rows, [("Width", "4 m"), ("Height", "2.5 m")])
        self.assertEqual(notes, "")


class ProductPageLayoutTests(TestCase):
    def setUp(self):
        self.material = Category.objects.create(
            name="Polycarbonate",
            slug="polycarbonate",
            group=Category.Group.MATERIAL,
        )
        self.sibling = Category.objects.create(
            name="Technical Plastics",
            slug="technical-plastics",
            group=Category.Group.MATERIAL,
        )
        self.product = Product.objects.create(
            sku="PC-MW-16",
            name="16 mm multiwall polycarbonate sheet",
            short_description="Multiwall sheet for roofs and façades.",
            full_description="Quoted per project for sheet size and quantity.",
            technical_text="Thickness – 16 mm - UV protection – Outer face",
            seo_title="16 mm multiwall PC sheet",
            seo_description="Multiwall polycarbonate sheet for industrial greenhouse roofs.",
            is_active=True,
        )
        self.product.categories.add(self.material)
        ProductSpecification.objects.create(
            product=self.product,
            label="Fire rating",
            value="B s1 d0",
            sort_order=10,
        )
        png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        ProductImage.objects.create(
            product=self.product,
            file=SimpleUploadedFile("a.png", png, content_type="image/png"),
            alt_text="Sheet sample",
            sort_order=0,
        )
        ProductImage.objects.create(
            product=self.product,
            file=SimpleUploadedFile("b.png", png, content_type="image/png"),
            sort_order=1,
        )
        ProductDocument.objects.create(
            product=self.product,
            file=SimpleUploadedFile("sheet.pdf", b"%PDF-1.4\n", content_type="application/pdf"),
            title="Technical data sheet",
        )
        self.related = Product.objects.create(
            sku="PC-SOLID-4",
            name="4 mm solid polycarbonate sheet",
            short_description="Solid sheet for guards.",
            is_active=True,
        )
        self.related.categories.add(self.material)

    def test_product_page_has_b2b_layout_and_seo(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, "application/ld+json")
        self.assertContains(response, "Inquire")
        self.assertContains(response, "16 mm multiwall PC sheet")
        self.assertContains(response, "Technical specifications")
        self.assertContains(response, "Fire rating")
        self.assertContains(response, "B s1 d0")
        self.assertContains(response, "Technical data sheet")
        self.assertContains(response, "PDF")
        self.assertContains(response, "Related products")
        self.assertContains(response, self.related.name)
        self.assertContains(response, "product-thumbs")
        self.assertContains(response, "Ask for a quote")
        self.assertContains(response, 'aria-label="Breadcrumb"')

    def test_category_page_has_count_and_related_topics(self):
        url = reverse("pages:solution_topic", kwargs={"group": "material", "slug": "polycarbonate"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2 published products")
        self.assertContains(response, "Technical Plastics")
        self.assertContains(response, "CollectionPage")
        self.assertContains(response, self.product.sku)
