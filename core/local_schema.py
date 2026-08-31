from django.core.management import call_command
from django.db import connection

CATALOG_APPS = ("pages", "products")

REQUIRED_COLUMNS = {
    "pages_page": ("created_at", "updated_at", "slug", "title", "heading"),
    "products_category": ("name", "slug", "group"),
    "products_product": ("sku", "name", "slug"),
}


def catalog_schema_is_current():
    """Return True when pages/products tables match the current models."""
    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))
        for table, columns in REQUIRED_COLUMNS.items():
            if table not in tables:
                return False
            existing = {
                column.name
                for column in connection.introspection.get_table_description(cursor, table)
            }
            if any(column not in existing for column in columns):
                return False
    return True


def rebuild_sqlite_catalog_tables():
    """Drop outdated pages/products tables and re-apply their migrations.

    Admin users and other apps are kept. SQLite only — this is for a leftover
    local db.sqlite3 from an older schema, not for production databases.
    """
    if connection.vendor != "sqlite":
        raise RuntimeError("rebuild_sqlite_catalog_tables() is only for SQLite.")

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND (name LIKE 'pages_%' OR name LIKE 'products_%')"
        )
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
        cursor.execute(
            "DELETE FROM django_migrations WHERE app IN ('pages', 'products')"
        )
        cursor.execute("PRAGMA foreign_keys = ON")

    for app_label in CATALOG_APPS:
        call_command("migrate", app_label, interactive=False, verbosity=1)
