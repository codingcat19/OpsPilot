# OpsPilot

AI-assisted DevOps operations platform that analyzes infrastructure, CI/CD pipelines, and production logs.

## Tech Stack

- **Frontend**: Next.js + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + SQLAlchemy + Alembic + Pydantic
- **Database**: PostgreSQL 16
- **AI Providers**: Gemini, Groq, Ollama (provider abstraction)
- **DevOps**: Docker Compose, GitHub Actions

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- Node.js 20+

### Using Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up -d db
docker compose exec backend uv run alembic upgrade head
docker compose up
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Install Dependencies

**Backend:**

```bash
cd backend
uv sync                # install all deps (runtime + dev)
```

**Frontend:**

```bash
cd frontend
npm install
```

### Local Development

**Backend:**

```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm run dev
```

### Database Migrations

**Local:**

```bash
cd backend
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"
```

**Docker:**

```bash
docker compose exec backend uv run alembic upgrade head
docker compose exec backend uv run alembic revision --autogenerate -m "description"
```

## Project Structure

```
opspilot/
├── backend/           # FastAPI application
│   ├── app/           # Application code
│   │   ├── api/       # API routes (v1)
│   │   ├── auth/      # Authentication module
│   │   ├── analyzers/ # Analysis engine + rule engine
│   │   ├── parsers/   # File parsers (Docker, Terraform, GH Actions)
│   │   ├── providers/ # AI provider abstraction
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   ├── repositories/ # Data access layer
│   │   └── core/      # Shared utilities
│   ├── tests/         # Pytest tests
│   └── alembic/       # Database migrations
├── frontend/          # Next.js application
│   └── src/           # Source code
│       ├── app/       # App router pages
│       ├── components/# React components
│       ├── lib/       # Utilities (API client, auth)
│       └── types/     # TypeScript types
├── docs/              # Design documents
└── docker-compose.yml
```

## Analysis Pipeline

```
Upload → Parser → Rule Engine → Findings → AI Explanation → Report
```

Supported file types (v1):
- Dockerfiles
- Terraform configurations
- GitHub Actions workflows

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/register` | User registration |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/projects` | Create project |
| POST | `/api/v1/analyze/docker` | Analyze Dockerfile |
| POST | `/api/v1/analyze/terraform` | Analyze Terraform |
| POST | `/api/v1/analyze/github-actions` | Analyze GH Actions |
| GET | `/api/v1/reports/{id}` | Get analysis report |

## Development

```bash
# Lint
cd backend && uv run ruff check .
cd frontend && npm run lint

# Test (requires running PostgreSQL)
cd backend && docker compose exec backend uv run pytest

# Format
cd backend && uv run ruff format .
```
