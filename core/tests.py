from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, TransactionTestCase

from core.local_schema import catalog_schema_is_current
from core.menu import find_topic
from pages.models import Page
from products.models import Category, Product


class MenuTests(TestCase):
    def test_find_topic(self):
        topic = find_topic("industry", "food-manufacturing")
        self.assertEqual(topic["label"], "Food Manufacturing")
        self.assertIsNone(find_topic("industry", "missing"))


class RebuildLocalSchemaTests(TransactionTestCase):
    def test_seed_rebuilds_stale_sqlite_tables_and_keeps_users(self):
        User = get_user_model()
        User.objects.create_superuser("keepme", "keep@example.com", "pass-keepme")
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("DROP TABLE pages_page")
            cursor.execute(
                """
                CREATE TABLE pages_page (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug varchar(120) NOT NULL UNIQUE,
                    title varchar(160) NOT NULL
                )
                """
            )
            cursor.execute("DROP TABLE products_category")
            cursor.execute(
                """
                CREATE TABLE products_category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug varchar(180) NOT NULL UNIQUE
                )
                """
            )
            cursor.execute("PRAGMA foreign_keys = ON")
        self.assertFalse(catalog_schema_is_current())
        call_command("seed_catalog", "--demo", verbosity=0)
        self.assertTrue(catalog_schema_is_current())
        self.assertTrue(User.objects.filter(username="keepme").exists())
        self.assertTrue(Page.objects.filter(slug="about").exists())
        self.assertTrue(Category.objects.filter(slug="polycarbonate").exists())
        self.assertTrue(Product.objects.filter(sku="PC-MW-16").exists())
