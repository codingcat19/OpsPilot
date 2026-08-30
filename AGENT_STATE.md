# AGENT_STATE.md — Current Session Context

> Last updated: 2026-08-12
> Branch: `main` (terraform analyzer added)

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
- **Docker analyzer pipeline implemented**:
  - `parsers/docker_parser.py` — line-based Dockerfile parser → `{instructions, stages}` (handles `\` continuations, comments, case-insensitive instructions, multi-stage `FROM ... AS`, `@digest`, `registry:port` tags)
  - `analyzers/rule_engine.py` — dispatcher; `docker` → `DockerAnalyzer`, other types return `[]` for now
  - `analyzers/engine.py` — `AnalyzerEngine.analyze(content, file_type)`: parse → `rule_engine.evaluate`; raises `ValueError` on unsupported file type
  - `analyzers/docker_analyzer.py` — 8 rules: missing USER (high), unpinned base tag (medium), hardcoded secret in ENV/ARG (critical), `ADD` over `COPY` (medium), pipe-to-shell (high), apt lists not cleaned (medium), pip cache left (medium), missing HEALTHCHECK (info), SSH port exposed (low)
  - 25 unit tests in `tests/test_docker_analyzer.py` — parser, each rule, engine end-to-end, rule engine dispatch
- **Terraform analyzer pipeline implemented**:
  - `parsers/terraform_parser.py` — HCL2 parser via `python-hcl2` dependency → `{resources, variables}`; normalizes quoted keys/values, strips `__is_block__` markers, preserves `${...}` expressions, raises on invalid HCL
  - `analyzers/terraform_analyzer.py` — 10 rules: public S3 ACL (critical), unblocked S3 public access (high), world-open security group (critical), unencrypted EBS/RDS/S3 (high), public RDS (high), secret variable default (critical), hardcoded credential in resource (critical), missing tags (low), default VPC (medium)
  - Registered in `engine.py` (`terraform: TerraformParser`) and `rule_engine.py` (`terraform: TerraformAnalyzer`)
  - `api/v1/analyze.py` — `POST /terraform` runs `AnalyzerEngine` and returns findings (HTTP 400 on invalid HCL); returns findings directly, not yet via service (matches docker stub pattern)
  - 27 unit tests in `tests/test_terraform_analyzer.py` — parser, each rule, engine end-to-end, rule engine dispatch
  - `test_docker_analyzer.py::test_engine_unsupported_file_type_raises` updated from `terraform` to `yaml` (terraform now supported)

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
- README.md updated with install deps, migrations (local + Docker), `uv` prerequisite

## What's Left / Known Issues

### Auth tests — RESOLVED
The asyncpg connection corruption issue that previously broke DB-touching auth tests is **fixed**. All 10 auth tests pass.

- **Root cause of original issue**: `repo.create()` calls `session.commit()` which commits the connection-level transaction, corrupting the asyncpg connection for subsequent tests
- **Fix applied**:
  1. `pyproject.toml` sets `asyncio_default_test_loop_scope = "session"` so all tests share one event loop (avoids cross-loop asyncpg connection reuse)
  2. `tests/conftest.py` adds a session-scoped `clean_database` autouse fixture that truncates all tables before the suite (tests were not isolated; stale rows caused duplicate-email 400)
- **Assertion fix**: `test_me_without_token` now asserts `401` (FastAPI `HTTPBearer` returns 401 for a missing token; 403 is only for deactivated users via `get_current_active_user`)

### Install dev deps in Docker for testing
```bash
docker compose exec backend uv sync --frozen --all-extras
```

### Auth gaps — known, not blockers
Authentication is complete for MVP. These are deferred improvements, note for when security is hardened:
- **No refresh token flow** — only single access token (JWT_EXPIRE_MINUTES default 1440). Add refresh token rotation when session-lifetime control is needed
- **No rate limiting on `/login` / `/register`** — vulnerable to brute-force and account enumeration. Add slowapi or similar middleware when exposed publicly
- **No logout / token revocation** — stateless JWT, valid until expiry. Acceptable for MVP; requires a denylist or short-lived tokens when revocation is needed

### Not yet implemented
- Project CRUD endpoints (skeleton exists in `api/v1/projects.py`, `projects/service.py`)
- File upload + analysis pipeline wiring — Docker + Terraform parsers/analyzers are done; `AnalysisService.run_analysis` (`services/analysis_service.py`) is still `NotImplementedError`, so no persistence, AI explanations, or report generation yet
- GitHub Actions parser (`parsers/github_actions_parser.py`) and analyzer (`analyzers/github_actions_analyzer.py`) — stubs
- Report generation
- Frontend→Backend integration (frontend uses placeholder URLs)
- Real AI provider integration (stubs exist in `providers/`)

## Quick Reference

### Run auth tests (local, DB in Docker)
```bash
docker compose up -d db                    # Postgres only
cd backend && uv sync --frozen --all-extras  # install dev deps once
uv run pytest tests/test_auth.py -v
```

### Run auth tests (Docker)
```bash
docker compose up -d db
docker compose build backend                 # rebuild to bake in current code
docker compose exec backend uv sync --frozen --all-extras   # first time only
docker compose exec backend uv run pytest tests/test_auth.py -v
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
| `backend/app/repositories/user_repository.py` | User CRUD — `create()` flushes only; commit owned by service layer |
| `backend/app/config.py` | Settings via pydantic-settings |
| `backend/app/database.py` | async engine + session factory |
| `backend/alembic/env.py` | Async Alembic env (async_engine_from_config) |
| `backend/alembic/versions/001_initial_schema.py` | Creates all 5 tables |
| `backend/tests/test_auth.py` | 10 auth tests — all passing |
| `backend/tests/test_docker_analyzer.py` | 25 Docker analyzer tests — all passing |
| `backend/app/parsers/docker_parser.py` | Dockerfile parser → instructions + stages |
| `backend/app/parsers/terraform_parser.py` | HCL2 parser via python-hcl2 → resources + variables |
| `backend/app/analyzers/terraform_analyzer.py` | 10 Terraform rules returning `Finding`s |
| `backend/tests/test_terraform_analyzer.py` | 27 Terraform analyzer tests — all passing |
| `backend/app/analyzers/engine.py` | `analyze(content, file_type)` — parse then run rules |
| `backend/app/analyzers/rule_engine.py` | Dispatch `file_type` → per-type analyzer |
| `backend/app/analyzers/docker_analyzer.py` | 8 Docker rules returning `Finding`s |
| `backend/tests/conftest.py` | `client` fixture + session-scoped `clean_database` truncation fixture |
| `frontend/src/lib/api.ts` | HTTP client (headers: `Record<string, string>`) |
| `frontend/src/lib/auth.ts` | Token storage helpers |
| `Dockerfile.backend` | Backend image — uses `uv run` for everything |
| `docker-compose.yml` | 3 services, no auto-migration |
| `opencode.json` | Git permission deny rules |
| `README.md` | Quick start, install deps, migrations |
| `AGENT_STATE.md` | This file — session context for agents |

## Conventions

- **No business logic in routes** — routes call services, services call repositories
- **Python type hints everywhere**
- **Backend container runs baked-in code (no volume mount)** — edit code → `docker compose build backend` before testing inside Docker, or run tests locally against the Dockerized DB
- **Tests run locally against Docker Postgres** (preferred): `docker compose up -d db`, then `cd backend && uv run pytest`
- **Never auto-commit** — suggest commit messages, let user run git commands
- **`uv run` prefix** — never activate venv manually; `uv run` handles it
- **Lockfile tracked in git** — `uv.lock` is committed, not ignored
