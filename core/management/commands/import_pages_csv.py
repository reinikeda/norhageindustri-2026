from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from tablib import Dataset

from pages.resources import PageResource


class Command(BaseCommand):
    help = "Import CMS pages from a CSV (default: docs/examples/pages.csv)."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default=str(settings.BASE_DIR / "docs" / "examples" / "pages.csv"),
            help="Path to a pages CSV keyed by slug",
        )

    def handle(self, *args, **options):
        path = Path(options["csv_path"])
        if not path.is_file():
            raise CommandError(f"No CSV file at {path}")
        dataset = Dataset().load(path.read_text(encoding="utf-8"), format="csv")
        result = PageResource().import_data(dataset, dry_run=False, raise_errors=True)
        self.stdout.write(self.style.SUCCESS(f"Imported {path.name}: {dict(result.totals)}"))
