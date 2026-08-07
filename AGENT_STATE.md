# AGENT_STATE.md — Current Session Context

> Last updated: 2026-08-07
> Branch: `main`
> Commit: `a6101bb fix: replace passlib with bcrypt and fix frontend TypeScript header type`

## What is OpsPilot?

AI-assisted DevOps platform. Users upload IaC files (Dockerfiles, Terraform, GitHub Actions), the system runs rule-based analysis, then optionally queries AI providers (Gemini/Groq/Ollama) for explanations, and generates a report.

**Tech stack**: FastAPI + SQLAlchemy(async) + Alembic + Pydantic v2 | Next.js (App Router) + TypeScript + Tailwind | PostgreSQL | Docker Compose

## What's Done

### Backend (`backend/app/`)
- **Project scaffolding**: all modules created (api, auth, analyzers, parsers, providers, models, schemas, services, repositories)
- **Database models**: User, Project, Analysis, Finding, Report — all defined in `models/analysis.py`, async SQLAlchemy
- **Auth system fully implemented**:
  - `auth/service.py` — `AuthService` with `bcrypt` (no passlib), JWT via `python-jose`
  - `auth/schemas.py` — `UserCreate`, `UserLogin`, `UserResponse`, `Token`
  - `api/v1/auth.py` — `POST /register` (201), `POST /login` (200), `GET /me` (200)
  - `api/deps.py` — `get_current_user`, `get_current_active_user`
  - User model has `is_active` field (default True)
- **Alembic**: async `env.py` using `async_engine_from_config`, initial migration `001_initial_schema.py` creates all 5 tables
- **Dependencies synced**: `uv.lock` matches `pyproject.toml` (`uv lock --check` passes)
  - `bcrypt>=4.0.0,<4.1.0` (replaced passlib, which is unmaintained)
  - `email-validator>=2.3.0` added for pydantic email validation
- **Tests**: `tests/test_auth.py` — 10 test cases written (see Known Issues)

### Frontend (`frontend/src/`)
- Next.js App Router pages: `/`, `/login`, `/register`, `/dashboard`
- `lib/api.ts` — HTTP client with typed headers (`Record<string, string>`)
- `lib/auth.ts` — auth token helpers
- `types/index.ts` — shared types
- **Build passes** (`npm run build` OK)

### Infrastructure
- `Dockerfile.backend` — CMD uses `["uv", "run", "uvicorn", ...]`
- `Dockerfile.frontend` — multi-stage Next.js build
- `docker-compose.yml` — backend, frontend, db services. No auto-migration.
- `.github/workflows/ci.yml` — CI pipeline
- OpenCode config: `opencode.json` with git permission rules
- OpenCode skills: architect, fastapi-expert, nextjs-expert, pr-reviewer, security-reviewer, technical-documentation, test-generator (all project-local in `.opencode/skills/`)

## What's Left / Known Issues

### Tests not passing against DB
- 7 of 10 auth tests fail with `OSError: Multiple exceptions` — they need a running PostgreSQL. Run via: `docker compose exec backend uv run pytest tests/test_auth.py -v`
- `test_me_without_token` asserts `403` but gets `401` — needs assertion fix in `tests/test_auth.py:116`: change `403` → `401`

### Unstaged changes
- Working tree is clean (all changes committed)

### Not yet implemented
- Project CRUD endpoints (skeleton exists in `api/v1/projects.py`, `projects/service.py`)
- File upload + analysis pipeline (skeleton exists in parsers/analyzers)
- Report generation
- Frontend→Backend integration (frontend uses placeholder URLs)
- Real AI provider integration (stubs exist in `providers/`)
- `pyproject.toml` run scripts: `alembic` and `alembic revision` need `uv run` prefix in commands

## Quick Reference

### Run auth tests
```bash
docker compose up -d db                          # start postgres
cd backend && docker compose exec backend uv run pytest tests/test_auth.py -v
```

### Fix the one test assertion
```bash
# tests/test_auth.py line 116: change 403 → 401
```

### Start dev (Docker)
```bash
docker compose up    # backend:8000, frontend:3000, db:5432
```

### Start dev (local)
```bash
cd backend && uv run uvicorn app.main:app --reload  # :8000
cd frontend && npm run dev                            # :3000
# PostgreSQL must be running on :5432
```

### Apply migrations
```bash
cd backend && docker compose exec backend uv run alembic upgrade head
```

### Make a new migration
```bash
cd backend && docker compose exec backend uv run alembic revision --autogenerate -m "msg"
```

## Key File Map

| File | What it does |
|---|---|
| `backend/app/auth/service.py` | AuthService — password hashing, JWT creation (bcrypt, no passlib) |
| `backend/app/auth/schemas.py` | UserCreate, UserLogin, UserResponse, Token |
| `backend/app/api/v1/auth.py` | Register, login, /me endpoints |
| `backend/app/api/deps.py` | `get_current_user`, `get_current_active_user` DI |
| `backend/app/models/analysis.py` | All SQLAlchemy models (User, Project, Analysis, Finding, Report) |
| `backend/app/config.py` | Settings via pydantic-settings |
| `backend/app/database.py` | async engine + session factory |
| `backend/alembic/env.py` | Async Alembic env (async_engine_from_config) |
| `backend/alembic/versions/001_initial_schema.py` | Creates all 5 tables |
| `backend/tests/test_auth.py` | 10 auth tests (7 need DB, 1 assertion to fix) |
| `frontend/src/lib/api.ts` | HTTP client (headers: `Record<string, string>`) |
| `frontend/src/lib/auth.ts` | Token storage helpers |
| `Dockerfile.backend` | Backend image — uses `uv run` for everything |
| `docker-compose.yml` | 3 services, no auto-migration |
| `opencode.json` | Git permission deny rules |

## Conventions

- **No business logic in routes** — routes call services, services call repositories
- **Python type hints everywhere**
- **Tests run inside Docker** (needs PostgreSQL): `docker compose exec backend uv run pytest`
- **Never auto-commit** — suggest commit messages, let user run git commands
- **`uv run` prefix** — never activate venv manually; `uv run` handles it
- **Lockfile tracked in git** — `uv.lock` is committed, not ignored
