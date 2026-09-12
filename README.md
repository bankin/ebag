# ebag

My solution to the provided interview task 

## Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — web framework.
- **[SQLModel](https://sqlmodel.tiangolo.com/)** — ORM models (built on SQLAlchemy + Pydantic).
- **[Alembic](https://alembic.sqlalchemy.org/)** — database migrations.
- **[pytest](https://docs.pytest.org/)** — the search endpoint's test suite runs against an in-memory SQLite DB, no Postgres required.
- **[uv](https://docs.astral.sh/uv/)** — dependency management and the way both the app and its dev tooling are run.

## Running it

### Option A — Docker Compose (recommended)

Starts Postgres and the app together; the container applies pending Alembic
migrations automatically before serving.

```bash
docker compose up --build
```

The API is then available at `http://localhost:8080` (docs at `/docs`).

To stop it: `docker compose down` (add `-v` to also drop the Postgres volume).

### Option B — Locally with uv

Requires a Postgres instance reachable at the URL below (or override
`DATABASE_URL`/`ALEMBIC_DATABASE_URL`, see **Configuration**).

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev
```

## Configuration

Everything is a `pydantic-settings` field in `app/config/settings.py`, so it
can be set via environment variable (see `docker-compose.yml` for the Docker
values) or left at its default for local development:

| Env var | Default | Purpose |
|---|---|---|
| `DEBUG` | `false` | Echoes SQL statements when `true`. |
| `DATABASE_URL` | `postgresql+asyncpg://root:some@localhost:5432/ebag` | App's async DB connection. |
| `ALEMBIC_DATABASE_URL` | `postgresql://root:some@localhost:5432/ebag` | Migrations' sync DB connection (separate driver from the app). |
| `IMAGE_STORAGE_DIR` | `data/images` | Where uploaded product images are written on disk. |
| `IMAGE_URL_PREFIX` | `/images` | URL path the images directory is served under. |

## Tests

```bash
uv run pytest
```

Only the search endpoint has tests, per the task's requirements — they run
against an isolated in-memory SQLite DB (`tests/conftest.py`), so no running
Postgres is needed.

