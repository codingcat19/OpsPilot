# AGENTS.md

## Key commands

```bash
# Backend
cd backend
uv run ruff check .           # lint
uv run ruff format .          # format
uv run pytest                 # test
uvicorn app.main:app --reload # dev server

# Frontend
cd frontend
npm run lint
npm run build
npm run dev

# Docker
docker compose up             # backend:8000, frontend:3000, db:5432

# Database
cd backend
alembic upgrade head
alembic revision --autogenerate -m "msg"
```

## Verification order

lint → typecheck → test

## Architecture

- **Modular monolith** backend with clear module boundaries per `CODING_STANDARDS.md`
- **No business logic in API routes** — routes delegate to services, services use repositories
- **DI pattern**: `app/api/deps.py` provides `get_db`, `get_current_user`
- **AI provider abstraction**: rule-based analysis first, AI explanations second
- **Pipeline**: Upload → Parser → Rule Engine → Findings → AI → Report

## Module layout (`backend/app/`)

| Module | Purpose |
|---|---|
| `api/v1/` | Route handlers (thin — no logic) |
| `auth/` | JWT auth, user model/schemas |
| `analyzers/` | `AnalyzerEngine` orchestrator + `RuleEngine` + per-type analyzers |
| `parsers/` | `BaseParser` ABC + per-type parsers |
| `providers/` | `BaseAIProvider` ABC + Gemini/Groq/Ollama |
| `models/` | SQLAlchemy models (User, Project, Analysis, Finding, Report) |
| `schemas/` | Pydantic request/response schemas |
| `services/` | Business logic (AnalysisService) |
| `repositories/` | Data access layer |

## Coding standards

- Python type hints everywhere
- Repository pattern for data access
- Structured JSON logging
- Keep parser, rule engine, and AI provider separate
- Unit tests for analyzers

## Design docs

All moved to `docs/`: PRD, ARCHITECTURE, TECH_STACK, DATABASE, API_SPEC, ANALYZER_ENGINE, CODING_STANDARDS, PROJECT_STRUCTURE.
