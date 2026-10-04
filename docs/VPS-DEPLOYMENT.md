# NCCT on an Ubuntu VPS

Prepared 5 October 2026 for this repository, `config.wsgi:application`, and `design.theadvoxy.com`.
These instructions target a fresh Ubuntu 24.04 LTS server with sudo access and a public IPv4 address. They are a deployment runbook, not evidence that a remote VPS has already been configured or tested. Commands below run in the VPS Bash terminal unless labelled otherwise. Replace `YOUR_VPS_IP` and password placeholders before use.

Architecture: Nginx handles HTTPS, Gunicorn runs Django on loopback, PostgreSQL holds content/enquiries, and `/var/lib/ncct/media` holds uploads outside the Git checkout. WhiteNoise continues serving collected static assets. A modest starting allocation is 2 vCPU / 2 GB RAM; monitor actual load and resize if needed.

## 1. Preserve existing production data before changing DNS

Keep Render running until the VPS passes acceptance checks. The seed commands supply starter data only; they do NOT copy existing Render enquiries, admin users, edited content or uploads.

If Render has production changes, first back up its database and media. For a PostgreSQL source, use a compatible `pg_dump` client and its authorised external connection from your workstation or VPS; no Render Shell is required. Keep the connection string/password private. Do not import a live database blindly over a populated target.

For an existing PostgreSQL database, restore into the **empty** VPS database created in step 3, **before** running migrations/seeds:

```bash
# First copy your privately created Render PostgreSQL backup to /srv/ncct/.
# The dump must be readable by ncct; never put it inside app/ or Git.
sudo -u ncct pg_restore -h 127.0.0.1 -U ncct -d ncct -W \
  --no-owner --no-privileges --exit-on-error /srv/ncct/render-backup.dump
```

Use a custom-format dump (`pg_dump -Fc`). If the source PostgreSQL major version is newer than the VPS version, install a compatible target/client before restoring. Transfer uploaded media separately into `/var/lib/ncct/media/`, preserving relative paths and `ncct:www-data` ownership. For existing S3 storage, keep the same authorised bucket settings instead of configuring local media. SQLite-to-PostgreSQL conversion needs a reviewed data export/import; do not copy a SQLite file into PostgreSQL or expect starter seeds to reproduce admin edits.

## 2. Connect and install packages

From your computer:

```bash
ssh YOUR_SSH_USER@YOUR_VPS_IP
```

On the VPS:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-venv python3-dev build-essential libpq-dev \
  postgresql postgresql-contrib nginx git curl ufw snapd
sudo systemctl enable --now postgresql nginx

# Add your actual SSH port first if it is not the standard port 22.
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status

sudo adduser --disabled-password --gecos '' ncct
sudo install -d -o ncct -g ncct -m 0755 /srv/ncct
sudo install -d -o ncct -g www-data -m 2750 /var/lib/ncct/media
sudo install -d -o root -g ncct -m 0750 /etc/ncct
```

Allow TCP 80/443 and your SSH port in the VPS provider's firewall too. Do not expose PostgreSQL 5432 or Gunicorn 8001 publicly. Retain a working SSH session while checking firewall access.

## 3. Create the PostgreSQL database

Generate a random database password, save it in your password manager, and enter it at the password prompt below. A hexadecimal password avoids URL escaping problems:

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
sudo -u postgres createuser --pwprompt ncct
sudo -u postgres createdb --owner=ncct ncct
```

The database role does not need superuser or database-creation privileges. PostgreSQL stays local. Restore existing PostgreSQL data now if applicable (step 1).

## 4. Clone and install the application

```bash
sudo -u ncct git clone --branch main --single-branch \
  https://github.com/AdnanUmmer/NCCT.git /srv/ncct/app
sudo -u ncct python3 -m venv /srv/ncct/venv
sudo -u ncct /srv/ncct/venv/bin/python -m pip install --upgrade pip
sudo -u ncct /srv/ncct/venv/bin/pip install -r /srv/ncct/app/requirements.txt
```

If GitHub requires authentication, use a read-only repository deploy key for the `ncct` account and clone with `git@github.com:AdnanUmmer/NCCT.git`. Do not embed a token/password in the clone URL. Do not replace an existing populated application directory with this fresh-install command.

## 5. Create the private environment file

Generate a separate Django secret:

```bash
python3 -c 'import secrets; print(secrets.token_hex(48))'
sudo touch /etc/ncct/ncct.env
sudo chown root:ncct /etc/ncct/ncct.env
sudo chmod 0640 /etc/ncct/ncct.env
sudo nano /etc/ncct/ncct.env
```

Paste and replace the two secret placeholders. Keep each assignment on one line. This syntax works with both systemd and Bash. Do not add `export` prefixes.

```ini
DJANGO_DEBUG=0
DJANGO_SECRET_KEY='REPLACE_WITH_THE_GENERATED_DJANGO_SECRET'
DATABASE_URL='postgresql://ncct:REPLACE_WITH_DATABASE_PASSWORD@127.0.0.1:5432/ncct'
DJANGO_ALLOWED_HOSTS=design.theadvoxy.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://design.theadvoxy.com
SITE_URL=https://design.theadvoxy.com
DJANGO_TRUST_PROXY_SSL=1
DJANGO_SSL_REDIRECT=1
DJANGO_HSTS_SECONDS=0
DJANGO_HSTS_INCLUDE_SUBDOMAINS=0
DJANGO_HSTS_PRELOAD=0
SITE_INDEXABLE=0
MEDIA_ROOT=/var/lib/ncct/media
ADMIN_LOGIN_RATE_LIMIT=20
```

Do **not** set `RENDER=true` on the VPS. `DJANGO_TRUST_PROXY_SSL=1` enables the existing forwarded-protocol setting. Nginx below overwrites that header; Gunicorn accepts connections only on loopback. Django can safely keep HTTPS redirection enabled with this configuration. Do not use Cloudflare Flexible SSL; use DNS-only for initial setup or Full (strict) after the origin certificate is installed.

`ncct.onrender.com` remains a Render-owned hostname; its DNS cannot be pointed at your VPS. Keep the Render app active if you still need that URL. Adding it to VPS ALLOWED_HOSTS cannot move it. A Render service kept active should retain its existing Render environment, not these VPS settings.

For optional SMTP, add provider values (quote passwords):

```ini
EMAIL_HOST=smtp.your-provider.example
EMAIL_PORT=587
EMAIL_HOST_USER='REPLACE_WITH_SMTP_USERNAME'
EMAIL_HOST_PASSWORD='REPLACE_WITH_SMTP_PASSWORD'
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL='REPLACE_WITH_VERIFIED_SENDER_ADDRESS'
ENQUIRY_NOTIFICATION_EMAIL='REPLACE_WITH_RECIPIENT_ADDRESS'
```

Omit these SMTP example lines entirely until configured. Enquiries still save in the database. For disk media, leave `AWS_STORAGE_BUCKET_NAME` unset. For existing S3 media, configure the AWS variables from `.env.example` and omit the local Nginx media aliases below.

The project does **not** automatically read `.env`; the following command wrapper and systemd service explicitly load this private file.

## 6. Add a management-command wrapper and initialize

```bash
sudo tee /usr/local/bin/ncct-manage >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd /srv/ncct/app
set -a
source /etc/ncct/ncct.env
set +a
exec /srv/ncct/venv/bin/python manage.py "$@"
EOF
sudo chmod 0755 /usr/local/bin/ncct-manage

sudo -u ncct ncct-manage check
sudo -u ncct ncct-manage migrate --noinput
sudo -u ncct ncct-manage seed_homepage
sudo -u ncct ncct-manage import_ncct_content
sudo -u ncct ncct-manage collectstatic --noinput
sudo -u ncct ncct-manage createsuperuser
```

The two initializers are safe to repeat: their initialization receipts preserve subsequent admin edits and deliberate deletions. On a new database they create the homepage, categories, capabilities, starter content, verified product models and resources. Bundled PDFs/static photographs arrive through Git, not database uploads. Existing user accounts can be retained by restoring the production database; create a new administrator only if needed.

## 7. Run Gunicorn with systemd

```bash
sudo tee /etc/systemd/system/ncct.service >/dev/null <<'EOF'
[Unit]
Description=NCCT Django website
After=network.target postgresql.service

[Service]
User=ncct
Group=www-data
WorkingDirectory=/srv/ncct/app
EnvironmentFile=/etc/ncct/ncct.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/srv/ncct/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8001 --workers 2 --timeout 60 --access-logfile - --error-logfile -
Restart=on-failure
RestartSec=5
UMask=0027
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ncct
sudo systemctl status ncct --no-pager

# This simulates the trusted HTTPS proxy without opening Gunicorn publicly.
curl -I -H 'Host: design.theadvoxy.com' \
  -H 'X-Forwarded-Proto: https' http://127.0.0.1:8001/
```

Expect HTTP 200. If it fails, inspect `sudo journalctl -u ncct -n 100 --no-pager` before continuing. Do not use `manage.py runserver` in production.

## 8. Configure Nginx

The following is for a fresh VPS. If it already hosts sites, preserve their configuration and ensure no other block claims this server_name. WhiteNoise serves `/static/` via Gunicorn; do not change Django's working static settings.

```bash
sudo tee /etc/nginx/sites-available/ncct >/dev/null <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name design.theadvoxy.com;
    client_max_body_size 25m;

    # Publication-controlled PDF downloads must pass through Django.
    location ^~ /media/documents/ {
        return 404;
    }

    # Public, validated image uploads. Never configure script execution here.
    location /media/ {
        alias /var/lib/ncct/media/;
        autoindex off;
        add_header X-Content-Type-Options nosniff always;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 65s;
    }
}
EOF
sudo ln -s /etc/nginx/sites-available/ncct /etc/nginx/sites-enabled/ncct
sudo nginx -t
sudo systemctl reload nginx
```

Do not repeat the symlink command if the link already exists. The raw admin file link for an uploaded PDF is intentionally unavailable through `/media/documents/`; use its public resource download route to test the published PDF. Unpublished PDFs must not be exposed through a broad media alias.

## 9. Move the custom-domain DNS and enable HTTPS

In the DNS zone for `theadvoxy.com`, replace the `design` CNAME pointing to Render with:

| Type | Name | Value |
|---|---|---|
| A | design | YOUR_VPS_IP |

Remove a stale AAAA record unless your VPS IPv6 is configured and working. Leave all other subdomains/mail records unchanged. An A record and CNAME cannot coexist at the same name. Lower the TTL ahead of the migration if desired. Keep Render available while old DNS caches expire.

Verify resolution from your computer, not only the VPS:

```bash
nslookup design.theadvoxy.com
```

Once DNS resolves to the VPS and ports 80/443 are accessible:

```bash
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo /snap/bin/certbot --nginx --redirect -d design.theadvoxy.com
sudo nginx -t
sudo systemctl reload nginx
sudo /snap/bin/certbot renew --dry-run
```

Enter your real email when Certbot asks. Certbot adds certificate settings and HTTP-to-HTTPS redirection. Snap schedules certificate renewal; the dry-run verifies the renewal path. Until the certificate is installed, Django will redirect HTTP to an HTTPS endpoint that is not yet ready: do not log into admin during that temporary setup interval. For a no-downtime cutover, preissue the certificate using your DNS provider's supported DNS-01 method before switching the A record.

## 10. Verify and launch

```bash
curl -I http://design.theadvoxy.com/
curl -I https://design.theadvoxy.com/
curl -IL --max-redirs 5 https://design.theadvoxy.com/
sudo -u ncct ncct-manage check --deploy
```

HTTP should redirect to HTTPS; HTTPS should return 200 without repeated redirects. In a browser, test `/`, `/products/`, a product detail, `/resources/`, a PDF download, `/contact/` and `/admin/`. Submit a real enquiry and verify its database/admin record; verify SMTP separately if configured. Upload a test image in admin, restart `ncct`, and confirm it is still visible. Test mobile navigation and the enquiry form. Do not assume the local automated checks validate remote DNS, PostgreSQL, disk permissions, SMTP or certificates.

Initially `check --deploy` warns about disabled HSTS (W004), subdomain HSTS (W005) and preload (W021). After confirming HTTPS, edit `/etc/ncct/ncct.env`:

```ini
DJANGO_HSTS_SECONDS=3600
SITE_INDEXABLE=1
```

Only enable indexing when public content/legal pages are approved. Then:

```bash
sudo systemctl restart ncct
sudo -u ncct ncct-manage check --deploy
curl https://design.theadvoxy.com/robots.txt
curl -I https://design.theadvoxy.com/sitemap.xml
```

W005/W021 remain deliberate unless the full domain hierarchy is ready for those policies. Do not silence unrelated warnings. Increase the HSTS duration later after operational verification. Submit the sitemap in Google Search Console after domain verification.

Known application limitation: the existing enquiry/login rate limiter uses `REMOTE_ADDR`. With this Nginx/Gunicorn arrangement, requests share the loopback proxy address, so the limits are shared (10 enquiry attempts / 10 minutes and 20 login attempts / 10 minutes by default). Forwarding headers alone do not change Django's REMOTE_ADDR. Before a busy public launch, implement and test an explicitly trusted-proxy client-IP policy or suitable edge throttling; do not blindly trust arbitrary incoming X-Forwarded-For. This guide does not claim that issue is solved by Nginx configuration.

## 11. Backups and maintenance

Back up both PostgreSQL and media, keep encrypted off-server copies, and perform a restore test. A backup on the same disk does not protect against loss of the VPS.

One-time/manual backup on the VPS:

```bash
sudo install -d -o root -g root -m 0700 /var/backups/ncct
sudo bash <<'EOF'
set -euo pipefail
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
runuser -u postgres -- pg_dump -Fc ncct > "/var/backups/ncct/database-$stamp.dump"
tar -czf "/var/backups/ncct/media-$stamp.tar.gz" -C /var/lib/ncct media
cp /etc/ncct/ncct.env "/var/backups/ncct/environment-$stamp.env"
EOF
```

The environment backup contains secrets: encrypt and restrict access. Schedule this with your backup system and define retention/off-server transfer; verify failure alerts. For an exact database/media point-in-time copy, pause writes during the backup. Keep the private files outside Git and outside web-served directories.

Prune expired rate windows and Django sessions daily:

```bash
sudo tee /etc/cron.d/ncct-maintenance >/dev/null <<'EOF'
17 3 * * * ncct /usr/local/bin/ncct-manage prune_rate_windows
27 3 * * * ncct /usr/local/bin/ncct-manage clearsessions
EOF
sudo chmod 0644 /etc/cron.d/ncct-maintenance
```

Check cron is installed/running (`sudo apt install -y cron`, `sudo systemctl enable --now cron`) and configure monitoring for maintenance failures. Keep Ubuntu security updates, PostgreSQL, Python dependencies and certificate renewals maintained.

## 12. Deploy later Git updates

Back up first (step 11). This simple procedure has a short maintenance window and must stop if any command fails; never restart automatically after a failed migration:

```bash
sudo bash <<'EOF'
set -euo pipefail
test -z "$(sudo -u ncct git -C /srv/ncct/app status --porcelain)"
sudo -u ncct git -C /srv/ncct/app rev-parse HEAD
systemctl stop ncct
sudo -u ncct git -C /srv/ncct/app pull --ff-only origin main
sudo -u ncct /srv/ncct/venv/bin/pip install -r /srv/ncct/app/requirements.txt
sudo -u ncct /usr/local/bin/ncct-manage check
sudo -u ncct /usr/local/bin/ncct-manage migrate --noinput
sudo -u ncct /usr/local/bin/ncct-manage seed_homepage
sudo -u ncct /usr/local/bin/ncct-manage import_ncct_content
sudo -u ncct /usr/local/bin/ncct-manage collectstatic --noinput
systemctl start ncct
EOF
sudo systemctl status ncct --no-pager
curl -I https://design.theadvoxy.com/
```

Save the previous commit ID and backup identifiers. A rollback involving schema changes may require a matching database restore; do not merely check out old code against incompatible migrations. This VPS procedure loads environment variables explicitly; running `bash build.sh` in a fresh shell without them will fail safely because no production secret is set.

## Troubleshooting

| Symptom | Check |
|---|---|
| 502 Bad Gateway | `systemctl status ncct`; `journalctl -u ncct -n 100`; Gunicorn bound to 127.0.0.1:8001 |
| Repeated HTTPS redirects | `DJANGO_TRUST_PROXY_SSL=1`, Nginx overwrites X-Forwarded-Proto with `$scheme`, restart service after env changes; no Cloudflare Flexible mode |
| DisallowedHost | The exact hostname in DJANGO_ALLOWED_HOSTS; no scheme/port/path; restart service |
| CSRF error | HTTPS origin in DJANGO_CSRF_TRUSTED_ORIGINS, scheme forwarding, actual form origin and cookies |
| Static 500/404 | Successful collectstatic and complete Git checkout; inspect Gunicorn logs; do not enable DEBUG |
| Uploaded image 403/404 | MEDIA_ROOT/alias match, traversable directories and ncct:www-data permissions; documents intentionally use application download routes |
| Missing catalogue content | Correct DATABASE_URL, migrations, initialization commands; use admin to republish deliberately unpublished records |
| Login/enquiry 429 | Existing shared proxy-address limiter described above; do not disable all rate protection |
| Database connection failure | `systemctl status postgresql`; database/user/password and URL escaping; local TCP authentication |
| Certificate failure | DNS A/AAAA, firewall port 80, Nginx server_name and provider/CDN proxy settings |

Useful logs:

```bash
sudo journalctl -u ncct -f
sudo tail -n 100 /var/log/nginx/error.log
```

## Reference documentation

- [Django 5.2 deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Gunicorn deployment](https://gunicorn.org/deploy/)
- [Certbot: Nginx on Linux with snap](https://certbot.eff.org/instructions?os=snap&tab=standard&ws=nginx)
- [Ubuntu TLS certificate guidance](https://ubuntu.com/server/docs/how-to/security/obtain-tls-certificates/)

Also review `PRODUCTION-HANDOVER.md` for unresolved client content and operational launch requirements.
