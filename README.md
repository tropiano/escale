# Escale

Members-only "private sales" on romantic boutique hotels for city weekends, for women travelling with a partner or friends.
It works like staycation.com, with the look of verychic.fr. Built for the Russian market: Russian at `/`, English at `/en/`.
Prices are in roubles. The demo data is fictional hotels in Moscow and St Petersburg.

**Stack:** Django 5.2 · PostgreSQL · Tailwind CSS v4 · WhiteNoise · Gunicorn. Ready for [Appliku](https://appliku.com).

## Prerequisites

You need:

- **Python 3.12 or newer**
- **PostgreSQL 14 or newer**, running locally
- **GNU gettext**, only if you edit the Russian translations

On macOS with Homebrew:

```bash
brew install python postgresql@15 gettext
brew services start postgresql@15
pg_isready -h localhost          # should print "accepting connections"
```

If `brew services` fails, or the log says "postmaster became multithreaded during startup", start Postgres by hand with a locale set:

```bash
LC_ALL=en_US.UTF-8 pg_ctl -D "$(brew --prefix)/var/postgresql@15" -l "$(brew --prefix)/var/postgresql@15/server.log" start
```

If you have two Homebrew installs (Intel in `/usr/local` and Apple Silicon in `/opt/homebrew`), use the one that owns Postgres. For example: `/usr/local/opt/postgresql@15/bin/pg_ctl -D /usr/local/var/postgresql@15 ...`.

The default `DATABASE_URL` (`postgres://localhost:5432/escale`) connects as your macOS user with no password, which is the Homebrew default. If your Postgres needs a user and password, change it in `.env`, for example `postgres://user:password@localhost:5432/escale`.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env
createdb escale                       # local Postgres must be running
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_escapes   # demo Moscow / St Petersburg hotels
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000 (Russian), http://127.0.0.1:8000/en/ (English) and http://127.0.0.1:8000/admin/.

To reload the demo data from scratch, run `manage.py seed_escapes --reset`.

## Styling (Tailwind)

The source is `assets/tailwind.css`, which holds the theme colours, fonts and button styles. The compiled file is `static/css/app.css`, and it is **committed**, so the server never needs Node or Tailwind.

```bash
.venv/bin/tailwindcss -i assets/tailwind.css -o static/css/app.css --watch    # while editing
.venv/bin/tailwindcss -i assets/tailwind.css -o static/css/app.css --minify   # before committing
```

## Translations

- **Interface text**: templates use English source strings, and the Russian is in `locale/ru/LC_MESSAGES/django.po`. After you change text, run:
  ```bash
  .venv/bin/python manage.py makemessages -l ru -i ".venv/*"
  # edit django.po, then:
  .venv/bin/python manage.py compilemessages -l ru -i .venv
  ```
  This needs GNU gettext (`brew install gettext`). Commit the `.mo` file too.
- **Hotel content**: every text field has a Russian version (for example `title`) and an English version (`title_en`), and both are editable in the admin. Templates read `obj.t.title`, which returns English on `/en/` and falls back to Russian when the English field is empty.

## Deploy on Appliku

The deployment is described in `appliku.yml`:

- **Build:** Python 3.13 image, app listens on port 8000.
- **Database:** a PostgreSQL 17 datastore called `db`. Its connection string is passed to the app as `DATABASE_URL`.
- **Environment:** `ALLOWED_HOSTS` is filled from the app's domains, `DEBUG=False`, and `SECRET_KEY` must be set by hand.
- **Processes:** `web` runs `bin/web.sh` (collects static files, starts Gunicorn). `release` runs `bin/release.sh` once after every deploy (applies migrations, loads the demo hotels if the database is empty).

First deploy:

1. In the Appliku dashboard, connect your GitHub account and a server (DigitalOcean, Hetzner, AWS, or any Ubuntu/Debian server you can SSH into).
2. Push this folder to a GitHub repo.
3. Install the CLI and log in:
   ```bash
   uv tool install appliku
   appliku login
   appliku teams list                      # note your team path
   appliku servers list --team <team>      # note the server id
   ```
4. Create the app and set the secret key:
   ```bash
   appliku apps create github <owner>/<repo> -t <team> -n escale -b main --server <server_id>
   appliku config set SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')" --team <team> --app <app_id>
   ```
5. Deploy and watch the logs:
   ```bash
   appliku apps deploy --team <team> --app <app_id>
   appliku deployments latest --team <team> --app <app_id>
   appliku apps logs --team <team> --app <app_id> --tail 200
   ```
6. Create an admin user from the app's console in the Appliku dashboard: `python manage.py createsuperuser`.
7. Optional, a custom domain: `appliku domains create --team <team> --app <app_id> --domain escale.ru`, then point the DNS at the server.

After that, every push to `main` can trigger a new deploy, if you turn on auto-deploy in the dashboard.

## Where things are

| Path | What |
|---|---|
| `stays/models.py` | `Destination`, `Escape` (an offer), `BookingRequest`, `Subscriber` |
| `stays/views.py` | Home, listing with filters, destination page, offer page with booking request |
| `stays/management/commands/seed_escapes.py` | Demo data (Moscow and St Petersburg) |
| `templates/` | Base layout, pages, card and newsletter partials |
| `config/settings.py` | All settings come from environment variables |

Booking requests and newsletter sign-ups are stored in the database and handled in the admin. No payment or email is sent yet.
