# AGENTS.md

## Status

This repo is **design documents only** — no source code, build config, or CI exists yet. The `frontend/`, `backend/`, `docs/`, and `.github/workflows/` directories from `PROJECT_STRUCTURE.md` are not yet created.

## Key design docs

| File | What it covers |
|---|---|
| `PRD.md` | Product requirements, phases, success criteria |
| `ARCHITECTURE.md` | Modular monolith, request flow, core modules |
| `TECH_STACK.md` | Next.js frontend, FastAPI backend, PostgreSQL, AI providers |
| `ANALYZER_ENGINE.md` | Pipeline: Upload → Parser → Rule Engine → Findings → AI → Report |
| `DATABASE.md` | Schema: users, projects, analyses, findings, reports |
| `API_SPEC.md` | REST endpoints under `/api/v1/` |
| `CODING_STANDARDS.md` | Type hints, SOLID, DI, repository pattern, no logic in routes |

## Architecture (from docs)

- **Backend**: FastAPI + SQLAlchemy + Alembic + Pydantic (modular monolith)
- **Frontend**: Next.js + TypeScript + Tailwind + shadcn/ui
- **AI**: Provider abstraction over Gemini, Groq, Ollama (rule-based first, AI explanations second)
- **Pipeline**: File upload → Parser → Rule Engine → Findings → AI explanation → Report
- **Auth**: JWT-based

## When code is added

Revisit this file. Expected commands to eventually document:
- Backend: `uvicorn` / `fastapi` dev server, `alembic migrate`, pytest
- Frontend: `npm run dev`, `npm run build`, `npm run lint`
- Docker: `docker compose up`
- Verification order: lint → typecheck → test
