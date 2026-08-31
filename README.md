# Norhage Industri Django project

This is a clean Django rebuild of the B2B catalog. The live public sites are still WordPress until this project is ready to replace them.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/

After the first migrate, load the menu categories and starter page copy:

```bash
python manage.py seed_catalog --demo
```

`--demo` adds a sample product (in two subcategories), two services, and one project. Re-running the command does not overwrite pages you have already edited.

If the homepage or `seed_catalog` fails with `no such column` (for example `pages_page.created_at` or `products_category.name`), the local `db.sqlite3` is from an older schema. Stop the server (`Ctrl+C`), then in PowerShell:

```powershell
python manage.py rebuild_local_schema
python manage.py seed_catalog --demo
python manage.py runserver
```

That rebuilds only the pages/products tables and **keeps your admin user**. If it still fails, start a new local database:

```powershell
Remove-Item .\db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_catalog --demo
python manage.py runserver
```

## Editing content

Use Django admin for day-to-day work:

- **Products** — SKU, text, several subcategories, photos, and PDFs
- **Categories** — industry / material / system topics (and optional child subcategories)
- **Pages** — heading, lead, body, and image for Home, Solutions, About, Wholesale, Contact, Quote, Services, Cases, Terms, Privacy, Cookies
- **Services** and **Projects** — list + detail pages

CSV import/export is on those same admin screens (Import / Export). Product categories in a CSV are category slugs separated by `|`. Test content scraped from the live English WordPress site:

- `docs/examples/products.csv` — 149 products (guessed categories, no images)
- `docs/examples/pages.csv` — Home, About, Wholesale, Contact, Services, Cases, Terms, Privacy, Cookies (rewrite before launch)

After `seed_catalog`:

```bash
python manage.py import_products_csv
python manage.py import_pages_csv
```

Or in admin: Products / Pages → Import. Re-importing updates by SKU or slug.

Public product URLs use the SKU: `/products/<sku>/`.

## What is in this repository

- `config/` — project settings, URLs, WSGI/ASGI
- `accounts/` — custom user model (staff only, no public signup)
- `core/` — shared context and error pages
- `pages/` — homepage, CMS pages, services, and projects
- `products/` — categories, products, images, and documents
- `quotes/` — contact and quote request forms (stored in admin, emailed to sales)
- `templates/` and `static/` — public layout
- `docs/PROJECT.md` — company facts, MVP, open decisions
- `docs/WORK_PLAN.md` — build sequence

Build order: English catalog → quotes → secure deploy → translations → extra domains → AI content tool.

## Tests

```bash
python manage.py test
python manage.py check
```
