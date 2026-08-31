# Agent notes

This is a Django 5 B2B catalog for Norhage Industri. GitHub is the source of truth.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Default settings module: `config.settings.dev`.
Custom user: `AUTH_USER_MODEL = accounts.User`. Create it before any other user-related migrations.

## Rules

- One work package per change set. Do not build the catalog, quote form, translations, or AI import until the current package is done.
- Do not add customer registration.
- Do not commit `.env`, `db.sqlite3`, `media/` uploads, or `staticfiles/`.
- Public product URLs will later use SKU: `/products/<sku>/`.
- Quotes must be stored in the database before email is sent.

## Checks before finishing a package

```bash
python manage.py check
python manage.py test
python manage.py migrate
```
