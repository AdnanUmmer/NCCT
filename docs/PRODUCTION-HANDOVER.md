# NCCT production handover — 3 October 2026

## Release status

Implementation and local QA are complete subject to the explicit launch blockers below. This is not a claim that a live Render deployment or external email/storage services were tested. No production database or Render dashboard was modified by this work.

The approved homepage composition, palette, hero, typography, scene imagery and enquiry interaction are preserved. The latest full-site brief restores Resources as the navigation destination. Visible branding remains NCCT.

## Delivered

- Server-rendered product catalogue, categories, search, combined data-backed filters, sorting, pagination and mobile filter dialog.
- Product detail pages with real model references, gallery support, editable specification rows/features, application relationships, related products/projects and actual PDF downloads.
- Verified-project listing/detail/gallery system. Unverified existing scene records cannot appear as delivered projects or in the project sitemap.
- Five application pages, About, Contact, Resources and editable operational privacy/cookie/website-information pages.
- Existing Homepage singleton extended into global site settings and homepage section visibility/headings. Existing contact values and content are preserved.
- Branded Django admin/login, product and project inlines, page/SEO management, publication/featured/order controls, resource upload/replacement and phone-friendly product tables.
- Enquiries retain validation, CSRF, honeypot, signed minimum-time tokens, database rate limiting and duplicate protection. Optional SMTP runs after the enquiry transaction commits; SMTP failure does not discard the submission.
- Database-backed admin-login throttling; safe PDF extension/content-type/header/size validation; image upload validation; normal Django authentication and permissions preserved.

## Data migrated

See [SOURCE-MIGRATION.md](SOURCE-MIGRATION.md) and the machine-readable `source-inventory/inventory.json` for all 58 visited source URLs and exclusions.

- **8 product records:** 3 preserved generic family previews plus 5 newly imported verified model products.
- **5 categories, 5 applications, 5 real datasheets.**
- **0 verified NCCT projects.** Three existing editorial images remain clearly distinguished from completed work.
- Original PDFs are bundled under `static/documents/`. Five corresponding product photographs were extracted from those PDFs and stored as WebP assets; PDFs were not replaced with screenshots.
- No LumoTubo case studies, foreign legal terms, client lists, awards or unsupported claims were imported.

## Content administration

1. Homepage: hero, introduction, heading overrides, visibility switches, logo, contact details, footer description and default SEO.
2. Content pages: About and legal/information pages. Their reserved slugs are `about`, `privacy`, `terms`, `cookies`; keep these stable because they are navigation destinations. Legacy legal fields remain in the database but are hidden from the Homepage editor to prevent conflicting editing locations.
3. Products: set category, model/reference, description, image/alt text and verified/published flags. Edit specifications/features/gallery inline. Unknown technical values must remain blank.
4. Resources: upload a PDF (maximum 20 MB), associate products/category, set type and publish. Replacing the upload takes precedence over the bundled original. Downloads are attachments with the correct PDF type. Remove associations/publication if a product/document is withdrawn.
5. Projects: publish only after attribution and image rights are verified. Set `attribution_verified` and `published`, then attach approved gallery images and any known products.
6. Solutions: manage application description, image, categories and product/project relationships.
7. Enquiries: authorised staff review saved messages and change their status. Create staff accounts with only required model permissions.

Use normal `python manage.py createsuperuser`. No production user/password is seeded. If Render Shell is unavailable, run the command locally against the production database's authorised external connection using private environment variables, or use an approved administrative machine. Never put passwords in build.sh or a public endpoint.

## SEO

- Unique page titles/descriptions; admin overrides; canonical links; social/Twitter previews with page-specific images.
- Breadcrumb navigation and BreadcrumbList JSON-LD. Factual Product schema has no invented prices, offers or ratings. Homepage Organization/LocalBusiness/WebSite information retains consistent contact details.
- Dynamic sitemap excludes drafts/unverified projects. Query-filter/search pages are noindex with a clean canonical URL.
- `SITE_INDEXABLE=0` by default for safe previewing; set `SITE_INDEXABLE=1` deliberately for the public launch. Robots includes the sitemap URL.
- Google and Bing verification fields are editable in Homepage. Analytics is not installed or silently enabled; if GA4 is later requested, configure consent and update the privacy/cookie disclosures before loading it.
- 301 redirects cover the NCCT homepage, category pages, lighting features, product-download page and contact page. Inherited third-party legal/case-study URLs are not misleadingly mapped to NCCT claims or the homepage. See `core/redirects.py`.
- The Instagram reel could not be retrieved. No claims are made about its recommendations. The implementation instead follows Google's Search Essentials and Django deployment guidance.

References: https://developers.google.com/search/docs/essentials and https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/.

## Deployment

Use the existing Render service and repository. Build Command:

```sh
bash build.sh
```

It installs dependencies, runs checks, migrates, runs both safe initializers, and collects static files. No Render Shell is needed for initialization.

Linux Start Command:

```sh
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -
```

Required production environment:

```ini
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<keep the existing long random secret>
DJANGO_ALLOWED_HOSTS=ncct.onrender.com,design.theadvoxy.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://ncct.onrender.com,https://design.theadvoxy.com
SITE_URL=https://design.theadvoxy.com
DATABASE_URL=<persistent PostgreSQL connection URL>
SITE_INDEXABLE=0
```

Render supplies `RENDER=true`. Django recognises `X-Forwarded-Proto: https` and keeps its own SSL redirect disabled on Render; the edge performs HTTPS redirection. No canonical-domain redirect was introduced. Both existing hostnames remain supported.

After HTTPS has been confirmed, set `DJANGO_HSTS_SECONDS=3600`, then raise it deliberately. `DJANGO_HSTS_INCLUDE_SUBDOMAINS` and `DJANGO_HSTS_PRELOAD` remain opt-in; do not preload an unverified domain hierarchy.

`check --deploy` with the documented Render settings reports W008 (edge HTTPS instead of Django redirect), W005 (subdomain HSTS not assumed), and W021 (preload not opted in). These are recorded intentional choices, not silenced warnings. With HSTS unset, W004 also correctly reminds the operator to enable it after HTTPS validation.

Persistent uploaded media on free Render requires external object storage. Configure:

```ini
AWS_STORAGE_BUCKET_NAME=<bucket>
AWS_ACCESS_KEY_ID=<private key id>
AWS_SECRET_ACCESS_KEY=<private secret>
AWS_S3_REGION_NAME=<region>
AWS_S3_ENDPOINT_URL=<S3-compatible endpoint, omit for AWS defaults>
```

The default S3 configuration is private with signed URLs and unique filenames. Static assets remain served by WhiteNoise. Do not make admin uploads public at the bucket level just to fix permissions. Confirm bucket policy, upload/download permissions and CORS requirements with the chosen provider. Actual remote upload/restart persistence needs the client's storage account; only local filesystem uploads and backend configuration were tested here.

Free Render instances have ephemeral filesystems. Local SQLite and uploaded local files cannot preserve live edits/enquiries across replacement. Use a persistent PostgreSQL service with backups and external media storage; do not rely on a temporary/trial database for a client launch. On a paid disk deployment, serve media through a suitable media service/proxy and run database initialization at runtime if the database itself is on the disk. Do not use build-time SQLite on a mounted runtime-only disk.

References: https://render.com/docs/free, https://render.com/docs/disks, https://django-storages.readthedocs.io/en/latest/backends/s3_compatible/index.html.

Optional SMTP variables: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`, `ENQUIRY_NOTIFICATION_EMAIL`. SMTP is optional for database persistence, but actual email delivery needs configured credentials and a verified sender.

## Security/operations notes

- Existing data and migration history are preserved; nullable slug columns are backfilled before unique constraints are applied. Both a fresh database and upgrade of a copy of the existing database were exercised.
- `homepage-v1` and `catalogue-v1` initialization receipts are atomic. Repeated deployments do not overwrite admin edits or restore deliberate deletions.
- Back up PostgreSQL and storage separately. Never delete initialization receipts to refresh content; edit through admin or write a reviewed import revision.
- The existing conservative rate limiter keys on the server's REMOTE_ADDR and does not trust arbitrary forwarded headers. Render may expose a shared proxy IP. Confirm the trusted client-IP forwarding path before launch and tune limits if required; do not blindly trust a user-controlled first X-Forwarded-For entry. Render documents the proxy behaviour at https://render.com/articles/how-render-handles-ddos-attacks.
- Schedule `python manage.py prune_rate_windows` through an appropriate maintenance runner. Enquiry retention/deletion policy must be approved by the client.
- This work does not configure production credentials, DNS, backups, external monitoring or real email delivery.

## Launch blockers / client inputs

| Missing item | Why it is not fabricated | Client action |
|---|---|---|
| Verified projects, roles, client/location/year details, approved photography | Old source captions are speculative or belong to LumoTubo | Supply signed-off project records and image rights; publish through admin |
| Final privacy/terms/cookie policy and retention decisions | Operational notices describe code behaviour, not approved legal obligations | Have authorised client/legal staff review and replace Content Pages |
| PostgreSQL + persistent media storage settings and backup ownership | No production account credentials are available | Provide/configure environment variables and verify restart persistence |
| Source datasheet conflicts and larger original product photographs | Contradictory values and low-resolution originals cannot be guessed away | Confirm the specific variants; provide current manufacturer originals |
| Current catalogue/company profile/certifications | No verified NCCT originals beyond the 5 datasheets were found | Supply approved PDFs if these download types are desired |
| Live performance and delivery acceptance | Local viewport checks do not measure actual Render cold starts, network latency or SMTP | Run staging/live Lighthouse and a real enquiry/email/storage check before launch |

Do not advertise a Lighthouse score: Lighthouse was not measured in this environment. Local static optimizations include an approximately 80 KB WebP hero, responsive image variants, explicit image dimensions, lazy loading below the fold, local fonts, deferred small JavaScript, WhiteNoise compression and related-object queries. The product list has a regression test enforcing a bounded query count.

## Verification evidence

`docs/qa/catalogue-responsive.json`: 28 real public pages × 9 widths (252 checks), no reported overflow, missing loaded images or duplicate H1s.

`docs/qa/site-audit.json`: 33 reachable public/document URLs, 19 referenced assets, no broken local links/assets/downloads.

45 automated tests pass. Automated tests cover existing enquiry/proxy behavior plus catalogue routes, combined filters, empty states, draft visibility, PDF content and upload validation, admin CRUD, image/PDF replacement, SEO/sitemap/robots, idempotent imports, SMTP failure and database-free 500 rendering. Browser QA uses an isolated disposable database for authenticated/admin/project test records; these records are not imported into the real content database.
