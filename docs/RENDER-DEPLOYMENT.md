# Render deployment

The complete current deployment and release checklist is in [PRODUCTION-HANDOVER.md](PRODUCTION-HANDOVER.md).

Build command: `bash build.sh`

The build installs dependencies and runs:

```sh
python manage.py check
python manage.py migrate --noinput
python manage.py seed_homepage
python manage.py import_ncct_content
python manage.py collectstatic --noinput
```

No Render Shell or separate manual seed step is needed. Both initializers preserve later admin edits and deliberate deletions.

Start command on Linux:

```sh
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -
```

Keep the existing main branch and service. Configure persistent PostgreSQL via DATABASE_URL and S3-compatible storage for uploads; free Render local storage is ephemeral. The build and application must connect to the same persistent database. Keep secrets out of Git.

Both ncct.onrender.com and design.theadvoxy.com must be present in DJANGO_ALLOWED_HOSTS and their HTTPS origins in DJANGO_CSRF_TRUSTED_ORIGINS. Render terminates HTTPS; Django trusts its scheme header and does not issue a second HTTPS redirect.

SITE_INDEXABLE defaults to 0 for preview safety. Enable it at the approved public launch. Read the handover for required variables, intentional deployment-check warnings, legal/content blockers and verification evidence.
