# Supabase / PostgreSQL deployment

Heat_Map uses SQLAlchemy and can run on **Supabase Postgres** with minimal changes.

## 1. Create a Supabase project

1. Create a project at [supabase.com](https://supabase.com).
2. Open **Project Settings → Database** and copy the **URI** connection string.
3. Use the **Session pooler** URL for SQLAlchemy if the app runs outside Supabase (recommended).

## 2. Configure the app

Set `DB_URL` (or `storage.db_url` in YAML):

```text
postgresql+psycopg2://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

Or in `.env`:

```env
DB_URL=postgresql+psycopg2://...
HEAT_MAP_ENV=prod
AUTH_SECRET_KEY=your-random-secret
```

Install dependencies (includes `psycopg2-binary`):

```bash
pip install -r requirements.txt
```

Start the API; `init_db()` runs `create_all()` on first boot.

For production, prefer applying [`001_initial_schema.sql`](../src/storage/migrations/001_initial_schema.sql) in the Supabase SQL editor instead of relying only on `create_all()`.

## 3. Row Level Security (optional)

If the dashboard talks to Supabase directly in the future, enable RLS using [`002_supabase_rls.sql`](../src/storage/migrations/002_supabase_rls.sql) as a starting point.

The **pipeline server** should use the **service role** connection (bypasses RLS) for high-volume `tracking_events` writes.

## 4. Alembic (recommended for production)

Schema changes after launch should use [Alembic](https://alembic.sqlalchemy.org/) migrations instead of editing `create_all()` only.

```bash
pip install alembic
alembic init alembic
# Point alembic.ini sqlalchemy.url to DB_URL, autogenerate revisions from src.storage.models
```

## 5. What stays local

- YOLO detection and camera ingestion still run on your machine or edge server.
- Supabase replaces **SQLite file storage** and optional **auth**; it does not process video frames.
