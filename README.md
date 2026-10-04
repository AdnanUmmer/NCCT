VPS hosting: see [the complete Ubuntu deployment guide](docs/VPS-DEPLOYMENT.md).

# NCCT corporate lighting website

Django catalogue, applications, verified projects, downloads, enquiries and content administration. The approved single-light homepage is preserved.

## Run locally

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements-dev.txt
# Export DJANGO_DEBUG=1 (PowerShell: $env:DJANGO_DEBUG='1')
python manage.py migrate
python manage.py seed_homepage
python manage.py import_ncct_content
python manage.py runserver
```

Environment files are not automatically loaded. See `.env.example`; never commit real credentials.

## Validate

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python manage.py test
python tools/audit_site.py
```

## Handover

- [Production handover, admin guide and launch blockers](docs/PRODUCTION-HANDOVER.md)
- [Source inventory and migration report](docs/SOURCE-MIGRATION.md)
- [Render commands](docs/RENDER-DEPLOYMENT.md)

The repository includes 5 reviewed Zoomled datasheets linked by the old NCCT site. It does not invent NCCT project delivery or republish unrelated LumoTubo case studies. Do not delete the seed/import receipts to refresh production content.

## Earlier homepage documentation

# NCCT DXB — homepage

A working, server-rendered Django homepage and enquiry workflow. No About, Projects, Products, Resources or Contact pages are implemented. Navigation points to real homepage sections; catalogue and project requests open the enquiry drawer.

## Run locally (PowerShell)

From `C:\Users\10adn\OneDrive\Documents\New project\ncct`:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:DJANGO_DEBUG = '1'
$env:DJANGO_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(50))")
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py seed_homepage
.venv\Scripts\python manage.py collectstatic --noinput
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/. The delivered local SQLite database is already migrated and seeded. No administrator password is included. Create your own administrator with `createsuperuser`.

If Windows `venv` cannot bootstrap pip, use the working global pip:

```powershell
python -m pip --python .venv\Scripts\python.exe install -r requirements.txt
```

`.env.example` documents configuration; the application intentionally reads process environment variables, not the file automatically. Development generates an ephemeral key if none is set, so restarting expires existing forms/sessions. Set a persistent secret for normal use.

## Structure

```text
ncct/
  config/                 settings, routes, WSGI
  core/                   homepage, capabilities, verified metrics, SEO
    management/commands/  seed_homepage, prune_rate_windows
    templatetags/         escaped JSON-LD rendering
    migrations/
  projects/               featured project content + attribution flag
  products/               lighting categories + verified product previews
  enquiries/              model, validation, anti-spam, POST endpoint, admin
  templates/
    base.html, home.html, 403.html, 404.html
    partials/             navigation, footer, enquiry, policy dialogs
    sections/             seven maintainable homepage sections
  static/
    css/site.css          design tokens + responsive components
    js/site.js            dialogs, categories, fetch form, navigation
    images/               locally stored, optimised NCCT source imagery
  media/                  administrator uploads (created on first upload)
  docs/
    CONTENT-AUDIT.md     provenance, reference study, missing content
    DESIGN.md            information architecture and design decisions
    QA.md                performed checks and limitations
    assets.json          exact image source URLs and dimensions
    qa/                  eight viewport screenshots + layout measurements
  fetch_assets.py         one-time source audit utility
  fetch_products.py       one-time catalogue import utility
  requirements.txt, requirements-dev.txt, .env.example
  manage.py
```

## Content administration

- **Homepage:** replace hero image, alt text, headline/copy, introduction, contact details and approved legal copy. Only one record is permitted. Use a line break to control headline composition.
- **Categories:** edit the five lighting applications, imagery and descriptions.
- **Projects:** edit image, name, location, application, source and ordering. A record is presented as a completed project only after its attribution flag is confirmed. Existing records are explicitly unverified lighting perspectives.
- **Products:** upload an image and enter a family or confirmed model, category, description and supported technical details. Only verified, featured records appear.
- **Capabilities:** edit the numbered expandable rows.
- **Verified metrics:** provide a source and explicitly publish. None are seeded because no reliable business metrics were found.
- **Enquiries:** search by company/name/email, filter by project type/date/status, update New → Contacted → Closed. Submitted personal information is read-only in the admin. No email is sent by this implementation; submissions are stored for staff review.

Use the upload field for replacements; `static_image` is the basename of a bundled source asset. Upload JPEG, PNG, WebP or AVIF under 5 MB, with descriptive alt text. Optimise replacement images before upload; automatic derivative generation for admin uploads is not included. Bundled images have small and full WebP variants. Missing image fields render an explicitly labelled development placeholder.

## Database and environment

SQLite is the local default. Set `DATABASE_URL=postgresql://user:password@host:5432/database` for PostgreSQL, then run `manage.py migrate` and `manage.py seed_homepage`. PostgreSQL support is configured but was not exercised against a live PostgreSQL server. Seeding is idempotent and preserves administrator edits.

For Render, set **Build Command** to `bash build.sh`. It installs dependencies, runs migrations, initializes homepage content, then collects static assets. Use the same persistent `DATABASE_URL` for build and runtime. See [Render deployment instructions](docs/RENDER-DEPLOYMENT.md), including SQLite limitations. Seeding now records a one-time initialization receipt; subsequent runs do not re-create renamed/deleted entries or reset admin publication choices. Existing populated sections are preserved on the first run too.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Required outside development; generate a unique secret, never commit it |
| `DJANGO_DEBUG` | `1` for local development; default `0` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames; local default `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins when required by deployment |
| `SITE_URL` | Canonical origin; default `https://ncctdxb.com` |
| `DATABASE_URL` | PostgreSQL connection; unset for SQLite |
| `DJANGO_SSL_REDIRECT` | Defaults on in production |
| `DJANGO_HSTS_SECONDS` | Defaults to one year in production; configure for your HTTPS rollout |
| `DJANGO_TRUST_PROXY_SSL` | Enable only behind a trusted proxy that replaces `X-Forwarded-Proto` |

Production should serve WSGI through Waitress/Gunicorn behind HTTPS. Waitress is included for Windows compatibility:

```powershell
.venv\Scripts\waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
```

Run `collectstatic` for versioned, compressed assets; WhiteNoise serves static files. Serve `media/` through your web server/object storage in production, without script execution, and back up media/database. Do not deploy the Django development server. Public deployment is not performed.

## Enquiry behaviour

`POST /enquiry/` supports JSON enhancement and ordinary HTML form submission. It implements CSRF, server validation, required contact consent, field limits, plain-text sanitisation, a hidden honeypot, a signed one-hour token with a three-second minimum age, database-backed limits of ten attempts per ten-minute window, UUID idempotency, and a unique keyed content fingerprint. Retrying the same submission is acknowledged without creating another record. Identical normalised enquiry content remains deduplicated while that record exists.

Only the server's `REMOTE_ADDR` participates in the keyed rate bucket; untrusted forwarded headers are ignored. Behind a reverse proxy configure a trusted mechanism to set the real remote address, or requests may share the proxy's limit. Rate counts are atomic database updates, shared across workers. Schedule `manage.py prune_rate_windows` daily. It removes expired rate records only. Decide and implement the enquiry retention period with NCCT before launch.

Optional Cloudflare Turnstile can be integrated through the `ENQUIRY_BOT_VERIFIER` dotted-callable setting in `config/settings.py`. Add the widget, verify tokens server-side with Cloudflare, set secrets via environment variables, and return a boolean. No CAPTCHA service or external dependency is currently called.

## Verification

```powershell
.venv\Scripts\python manage.py check
.venv\Scripts\python manage.py collectstatic --noinput
.venv\Scripts\python manage.py test
.venv\Scripts\python manage.py makemigrations --check --dry-run
node --check static/js/site.js
```

See [QA results](docs/QA.md). The 21 automated tests and browser checks pass. Lighthouse targets are not claimed as achieved: a Lighthouse run, real-device checks and production Core Web Vitals measurement remain outstanding.

## Production inputs and Phase 2

The homepage is implemented, but publication needs the missing content listed in [CONTENT-AUDIT.md](docs/CONTENT-AUDIT.md): the new brand pack/Figma references, confirmed NCCT project credentials and photography, product names/data sheets, approved legal copy, and any verified statistics. Source imagery is labelled without implying completed NCCT work.

Phase 2 can add About, project index/case studies, product discovery/details, solution pages, downloads/resources, Contact, approved legal pages, Arabic/RTL if requested, email/CRM delivery and production hosting. No routes or pages for these have been built in this phase.
