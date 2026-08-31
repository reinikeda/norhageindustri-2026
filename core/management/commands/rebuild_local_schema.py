from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

from core.local_schema import catalog_schema_is_current, rebuild_sqlite_catalog_tables


class Command(BaseCommand):
    help = (
        "Rebuild pages/products tables on a leftover local SQLite database. "
        "Keeps admin users. Do not use on production."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Rebuild even if the schema already looks current.",
        )

    def handle(self, *args, **options):
        if connection.vendor != "sqlite":
            raise CommandError("This command is only for the local SQLite database.")
        try:
            call_command("migrate", interactive=False, verbosity=1)
        except (OperationalError, ProgrammingError) as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"migrate could not update the existing tables ({exc}). Rebuilding catalog tables."
                )
            )
            rebuild_sqlite_catalog_tables()
        if options["force"] or not catalog_schema_is_current():
            self.stdout.write("Rebuilding pages, products, and quotes tables. Admin users are kept.")
            rebuild_sqlite_catalog_tables()
        if not catalog_schema_is_current():
            raise CommandError("Catalog tables are still missing columns after rebuild.")
        self.stdout.write(self.style.SUCCESS("Local catalog schema is ready."))
