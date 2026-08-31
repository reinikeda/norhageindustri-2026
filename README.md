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

## What is in this repository

- `config/` — project settings, URLs, WSGI/ASGI
- `accounts/` — custom user model (staff only, no public signup)
- `core/` — shared context and error pages
- `pages/` — homepage and informational pages
- `products/` — stub for the catalog (next work package)
- `quotes/` — stub for quote requests (after the catalog)
- `templates/` and `static/` — public layout
- `docs/PROJECT.md` — company facts, MVP, open decisions
- `docs/WORK_PLAN.md` — build sequence

Build order: English catalog → quotes → secure deploy → translations → extra domains → AI content tool.

## Tests

```bash
python manage.py test
python manage.py check
```
