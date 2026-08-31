# Work plan — verdict and revised sequence

## Verdict

**Yes. Use this plan, with a shorter sequence and a few hard cuts.**

The original document is directionally right:

- English catalog first, then quotes, then a secure deploy, then translations, then extra domains, then the AI writing tool
- No customer accounts, CRM, PDF quotations, or seven languages in the first launch
- Quote line-item snapshots, database-before-email, and “do not auto-publish AI drafts” are the correct B2B rules
- Checkpoints at the end of each step will keep separate chats from drifting

Do **not** follow it as eighteen phases and seventeen separate chats. That will recreate the same site several times with inconsistent models. This repo is also empty: there is no healthy `core` / `accounts` / `pages` / `products` project to audit here.

The rest of this file is the plan to actually follow. Company facts and open decisions live in [PROJECT.md](PROJECT.md).

## What to change from the original plan

1. **Start clean in this repository** unless the Cursor test code is pushed here and passes `manage.py check`. Do not design around apps that are not in git.
2. **Collapse 18 phases into 6 work packages.** Same order, less ceremony.
3. **Put production-safe settings in package 1**, not in a late “security phase”. CSRF, env secrets, `ALLOWED_HOSTS`, and `DEBUG` handling are project setup, not a feature.
4. **Skip a standalone design-system phase.** Build the base template while building the homepage. Restyle once the catalog exists.
5. **Do not build an accounts product.** A custom user model is required. Roles, assignments, and organizations are not.
6. **Simplify quote statuses.** Launch with `new` / `in_progress` / `closed`. The seven-status pipeline is a CRM.
7. **Treat documents as core.** This business already sells with spec PDFs. Media + PDF upload belongs in the first product model.
8. **Include a multi-product quote basket in MVP.** The original plan deferred it and then listed “multiple products” as a completion gate. Pick the basket.
9. **Plan WordPress cutover.** This is a replacement of live country domains, not a greenfield brochure. Redirects and URL inventory belong with the English catalog, not as a last SEO polish.
10. **Keep translations out of MVP, but freeze two decisions now:** custom translation tables (not parler), and SKU-based public URLs. That avoids a painful Phase 7 rewrite without building seven languages today.
11. **Do not translate legal pages as if they were marketing copy.** Company name, address, phone, and privacy entity change by domain.
12. **Host and email providers are Phase 0**, not launch-week surprises.

## Work packages (use one chat per package)

For every chat, paste:

- this file and `docs/PROJECT.md`
- the app being changed
- whether migrations are allowed
- the completion gate below

At the end of every package: commit, backup/export if the database has real content, and do not refactor unrelated apps.

### Package 1 — Foundation

Create the Django project in this repo.

Apps:

- project config (`config` or `norhageindustri`)
- `core` (shared utilities, context processors, error templates)
- `accounts` (custom user only)
- `pages` (stub)
- `products` (stub)
- `quotes` (stub, not implemented yet)

Must include:

- Custom user model **before** the first user migration
- Split settings (dev vs production)
- `.env` / environment variables, never commit secrets
- PostgreSQL-ready database config; SQLite only for local convenience
- Static files, media uploads, basic logging
- Admin at a non-obvious URL in production settings
- Base template: header, logo, nav, mobile nav, footer, buttons, forms, alerts
- 404 and 500 templates

Completion gate:

- `python manage.py check` passes
- migrate works
- admin login works with the custom user
- base template renders on desktop and mobile
- git history exists in this repo

Do not implement catalog views yet.

### Package 2 — English pages + catalog

`pages` and `products` only.

Pages (templates or a simple `Page` model — no CMS):

- Home, About, Services, Contact, Terms, Privacy, Cookies

Homepage should reuse the live English structure: introduction, product groups, services, proof/projects teaser, quote CTA, contact.

Products:

- `Category` and `Product` as specified in `PROJECT.md`
- Images and PDF documents
- Admin that a non-developer can use
- Public category list, product list, product detail
- Unpublished products return 404
- SKU-based product URLs
- Basic search by name/SKU if it stays simple
- Inventory of important current WordPress URLs for later redirects

Completion gate:

- Editor can publish a real product with image + PDF without touching code
- Public site hides unpublished products
- Every page has a real title, meta description, and working nav
- No placeholder “lorem” copy on pages intended for launch

### Package 3 — Quotes + email

Implement `quotes` after the catalog is browsable.

Public:

- Quote basket (session) for multiple products and quantities
- Quote form on product pages and a dedicated request page
- Validation, confirmation page
- Honeypot + rate limiting (and CAPTCHA if spam appears)

Admin:

- List/filter/search by company, email, status, date
- Line items visible
- Status + internal notes

Email:

- Sales notification
- Customer confirmation
- Reply-To = sales inbox
- Console backend in development; real provider in staging/production

Completion gate:

- Valid quote is stored even if SMTP fails
- Invalid email and missing fields are rejected
- Quantity must be a positive integer
- Duplicate rapid submits are limited
- Form works on a phone
- Contact form still works for non-product messages

### Package 4 — Staging deploy and English launch prep

Do this **before** translations.

- Production settings: `DEBUG=False`, secure cookies, HTTPS, `ALLOWED_HOSTS`, secrets in env
- Media upload type/size limits
- Database backups and one successful restore test
- Staging URL with real-ish content
- Error logging
- XML sitemap, robots, canonical URLs, Open Graph
- Redirect map from current English WordPress URLs
- Spam protection verified on staging with a real form submit

Completion gate: English staging can be shown to a salesperson, and they can complete “find product → request quote → see it in admin → receive email”.

Go live on norhageindustri.com only when that gate passes. Keep the other six domains on WordPress until English is stable.

### Package 5 — Translations + one extra domain

Only after English is earning quotes.

Data model:

- `Product` keeps SKU, images, documents, category, active flag
- `ProductTranslation` (and category/page equivalents) holds name, slug, descriptions, SEO, status
- Status per language: `missing` / `draft` / `needs_review` / `approved` / `published`
- Unpublished translations do not appear on that domain
- No English fallback on product pages

Routing:

- Domain selects language
- Test English + **one** other domain first (Lithuanian or Norwegian)

Also translate nav, forms, emails, and buttons. Keep a small terminology glossary for later AI use.

Completion gate: the same SKU on `.com` shows English and on the second domain shows the other language, or 404 if not published.

Then add the remaining domains one at a time.

### Package 6 — External content tool, then extras

After humans can already draft, review, and publish in Django:

1. CSV/JSON export-import of translation drafts
2. Authenticated API that creates/updates translations as `draft` only, never `published`
3. Organizations/contacts if quote volume needs it
4. News and projects apps
5. PDF quotations / customer accounts / CRM only with a real sales request

## Explicitly out of the first coding chats

- django-parler
- Customer registration
- Wagtail/CMS
- Celery (not needed until email/import volume says so)
- Headless SPA / React frontend
- Per-product attribute matrices
- Auto-publish from AI
- Building all seven domains in parallel

## Recommended chat order

1. Foundation (package 1)
2. Pages + products (package 2)
3. Quotes + email (package 3)
4. Staging / security / SEO / redirects (package 4)
5. Translation models + second domain (package 5)
6. External tool, then optional apps (package 6)

That is the original rule, kept:

**English catalog → quote workflow → secure deployment → translations → domains → external AI content integration**
