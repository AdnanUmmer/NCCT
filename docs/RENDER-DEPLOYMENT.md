# Render homepage initialization

Set the existing service's **Build Command** to:

```bash
bash build.sh
```

Keep the existing Start Command. The script installs requirements, checks Django, and runs in fail-fast order:

```bash
python manage.py migrate --noinput
python manage.py seed_homepage
python manage.py collectstatic --noinput
```

The build and running service must use the same persistent production database through `DATABASE_URL` (normally Render PostgreSQL). Keep credentials in Render environment variables. Do not commit `.env` or `db.sqlite3`.

## What is created

On an empty database: one Homepage using the single-light hero, five Categories, three featured Projects, three featured and verified Products, and four Capabilities. No metrics are seeded because no verified statistics exist. No users, passwords, enquiries, or uploaded media are seeded. Static image configuration is unchanged.

## Repeat-run protection

`core.HomepageSeedState` stores the `homepage-v1` initialization receipt. The receipt and starter records are written in one database transaction; any failure rolls back both. Once successful, later invocations exit without changing content. Renames, image replacements, publication flags, ordering, custom copy and deliberate deletions are preserved.

For an existing database without a receipt, each populated section is treated as administrator-owned and left alone. Empty sections are initialized. Existing Homepage content is preserved by `get_or_create(pk=1)`. Populated but incomplete sections are not topped up automatically, because doing so could reintroduce content an administrator intentionally removed or renamed.

If Products is empty but existing Categories no longer contain the required original category names, initialization fails without writes instead of attaching products to an arbitrary category. Add the intended products through admin and rerun. The seed command is an initializer, not an ongoing content synchronizer or reset command.

## Existing deployment

After deploying this commit with `bash build.sh`, no separate manual seeding step is necessary if the build and app share the same persistent database. To initialize the currently running production database immediately after the new code is available, run in Render Shell:

```bash
python manage.py migrate --noinput
python manage.py seed_homepage
```

Repeated runs are safe. Verify the deploy log says either `Homepage initialized` or `Homepage already initialized`.

## SQLite and persistence

If `DATABASE_URL` is unset, this project uses SQLite in the application directory. That database is not in Git. Build-time seeding can populate a new build's SQLite file, but it does **not** preserve later administrator edits or enquiries across replacement of an ephemeral filesystem. The initialization receipt cannot preserve a database that has itself been discarded. Use persistent PostgreSQL for normal Render deployment.

For an explicitly configured SQLite database on a Render persistent disk, the disk is unavailable during build/pre-deploy. Run migrations and seeding at runtime against the mounted disk before starting the server, rather than using this combined build script for database tasks. No database/storage migration or Render dashboard changes were performed by this code change.

References: https://render.com/docs/deploys and https://render.com/docs/disks.
