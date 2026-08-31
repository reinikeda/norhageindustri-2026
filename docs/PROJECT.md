# Norhage Industri — Project brief (Phase 0)

Status: proposed from the live WordPress sites and this empty GitHub repo. Confirm the **Open decisions** section before writing models.

## Identity

| Item | Value |
|---|---|
| Project name | norhageindustri-2026 |
| Public brand | Norhage Industri |
| Parent company | TEHI AS (Norway). Related entities appear on country sites (TEHI Filial Sverige, TEHI UG, TEHIS UAB). |
| Default language | English |
| Main domain | norhageindustri.com |
| Quote notification email | `info@norhageindustri.com` (`SALES_NOTIFY_EMAIL`) |
| B2C webshops (out of scope) | norhage.com, norhage.no, norhage.se, and related consumer shops |

This repository currently contains only the initial GitHub files. There is **no Django project here**. Any test apps in a local Cursor/VS Code folder should be treated as a reference, not as the production start, unless they are copied in and audited in the next chat.

## Language domains (existing public sites)

These already exist on WordPress. They are the seven future language versions, not a new idea.

| Language | Code | Domain |
|---|---|---|
| English | `en` | norhageindustri.com |
| Norwegian | `no` | norhageindustri.no |
| Swedish | `sv` | norhageindustri.se |
| Danish | `da` | norhageindustri.dk |
| Finnish | `fi` | norhageindustri.fi |
| German | `de` | norhageindustri.de |
| Lithuanian | `lt` | norhageindustri.lt |

Launch English first. Add one second domain only after the English catalog and quote form are live. Do not turn on all seven at once.

Legal pages are **not** a translation problem only. Contact details, company names, and addresses differ by country. Store those as per-domain settings, not as translated strings on a single About page.

## What this website is

A B2B catalog and inquiry site for industrial greenhouse systems, technical plastics, polycarbonate, rubber, profiles, fasteners, and related services. Buyers request quotes. Prices are not shown in the public catalog.

The current public site is WordPress. Typical buyer path today:

1. Land on a country domain
2. Browse categories / product pages
3. Submit a generic contact form (name, email, phone, subject, message)

The Django MVP should keep that path, and improve it: a quote can include specific products and quantities.

## MVP (English launch)

Must ship:

- English website on norhageindustri.com
- Homepage and informational pages (About, Services, Contact, Terms, Privacy, Cookies)
- Product categories and product catalog
- Product detail pages
- No public prices
- Ask-for-a-quote form, including selected products and quantities
- Django admin for pages, categories, products, quotes
- Email notification to sales + confirmation to the sender
- Basic SEO (titles, meta descriptions, clean URLs, sitemap, robots)
- HTTPS production deploy, backups, spam protection on public forms

Must not ship in MVP:

- Customer accounts / login
- Seven live language domains
- External AI content tool
- CRM
- Per-product attribute engine
- Formal PDF quotations
- News or case-study apps (the current Projects page can stay a simple static/admin page)

## Post-MVP

In this order, only after English is live:

1. Translation data model and human publish workflow
2. One extra language domain as a proof (recommended: Lithuanian or Norwegian)
3. Remaining language domains
4. Manual export/import of translation drafts, then an API for the external writing tool
5. Company/contact records if quote volume needs it
6. News and project/case-study apps
7. Quote PDFs, customer accounts, CRM — only if sales actually needs them

## Product categories (from the live sites)

Use this as the starting taxonomy. Nested categories only if the live catalog already needs them.

- Commercial / industrial greenhouses
- Technical plastics
- Polycarbonate sheets and systems
- Rubber materials
- Profiles
- Fasteners and construction materials
- Greenhouse film / related agricultural products (strong on the LT site)
- Services (assembly, repair, cutting, machining, bending) — these may be pages, not products

Wholesale-style SKUs already on the English site (sealing tapes, automatic vent openers) are good first catalog entries: they have names, variants, and PDF spec sheets.

## Required product fields (MVP)

Shared, language-neutral:

- SKU / product code (unique, required)
- Category
- Main image
- Extra images (optional)
- Technical documents / PDFs (first-class, not optional afterthought)
- Active / unpublished
- Featured (optional)
- Created / updated timestamps

English content (MVP; later moved or duplicated into translation rows):

- Name
- Slug
- Short description
- Full description
- Technical text
- SEO title and meta description
- Image alt text

Do not build a generic EAV attribute system in MVP. Variant details (roll width, sheet thickness, opener model) can live in the technical text and documents until a real pattern appears.

Unpublished products must be hidden from the public site and return 404, not a “coming soon” page.

## Required quote fields (MVP)

Request:

- Name
- Company
- Email
- Phone
- Country
- Message
- Source URL / domain
- Status (`new`, `in_progress`, `closed` is enough for launch)
- Internal notes
- Created timestamp

Each line item:

- Product (FK, nullable if the product is later deleted)
- Quantity (positive integer)
- Product name snapshot
- SKU snapshot
- Customer note (optional)

Store the row in the database **before** sending email. Email is a notification, not the system of record.

A session quote basket is not required for launch. The quote page accepts several product lines (SKU + quantity) on one submit, which matches how B2B buyers inquire for sheets, tapes, and fasteners. A later cart can remember lines while browsing.

Do **not** include assigned staff, seven CRM statuses, or export tools in MVP.

Also keep a separate Contact form for non-product questions (same spam protection, different destination label).

## Admin users

| Role | Access | Who |
|---|---|---|
| Superuser | full admin | **TBD** |
| Catalog editor | products, categories, pages, documents | **TBD** |
| Sales | quote requests, status, notes | **TBD** |

No public registration. Staff accounts only, created by an existing admin.

## Launch criteria (English)

The site is ready to replace WordPress English when:

- A non-technical editor can create a category, product, image, and PDF and publish them
- An unpublished product is not reachable by URL
- A visitor can add products and quantities, submit a quote, and see a confirmation
- Sales receives the email and can open the same request in admin
- If email delivery fails, the quote is still stored
- Forms reject empty required fields, bad emails, and obvious spam
- Homepage, About, Services, Contact, legal pages have real copy (no placeholder text)
- HTTPS, `DEBUG=False`, secrets in env, backups tested once
- Current WordPress English URLs that have traffic have redirects or equivalent new URLs listed

## Open decisions

Answer these before the first models are written:

1. **Hosting:** recommended default is PostgreSQL + one app host (for example Hetzner, Fly, Render, or a small VPS) + object storage for media (S3-compatible) + a transactional email provider (Postmark, Mailgun, or similar). Confirm.
2. **Who receives quote emails?** One inbox or country-specific inboxes even on the English site?
3. **Who edits products?** One person or several?
4. **Keep or change WordPress URLs?** A short inventory of current product/category URLs is needed for redirects, or SEO will drop on cutover.
5. **Is the local Cursor test code worth importing?** If it has a custom user model and working admin, paste or push it here for an audit. If it is experimental, start clean in this repo.
6. **Services:** products, pages, or both?
7. **Default from-address** for customer confirmation emails.

## Technical defaults (lock unless there is a reason not to)

- Django LTS, PostgreSQL in staging/production, SQLite acceptable only for local experiments
- Custom user model in `accounts` from the first migration, but **no** customer login
- Explicit translation models later, not django-parler (better fit for an external draft-import tool)
- Public product URLs include the SKU so later translated slugs do not force a redesign: `/products/<sku>/`
- Domain → language mapping, not `Accept-Language` and not a `/en/` path prefix
- Missing translations stay unpublished on that domain (no English fallback on technical product pages)
- WhiteNoise or equivalent for static files; media never served as an unchecked public dump
- Environment-based settings (`DJANGO_SETTINGS_MODULE` or a split `settings/dev.py` + `settings/prod.py`)
