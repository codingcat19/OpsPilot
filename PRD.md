# OpsPilot -- Product Requirements Document (PRD)

## Vision

OpsPilot is an AI-assisted DevOps operations platform that analyzes
infrastructure, CI/CD pipelines, and production logs to help engineers
identify, explain, and resolve issues faster.

## Goals

-   Analyze Dockerfiles, Terraform, GitHub Actions, and log files.
-   Combine deterministic rule-based analysis with LLM explanations.
-   Remain usable with free AI providers (Gemini, Groq, Ollama).
-   Demonstrate production-grade engineering and DevOps practices.

## Target Users

-   DevOps Engineers
-   Platform Engineers
-   SREs
-   Students learning DevOps

## Core Features (v1)

1.  Authentication (JWT)
2.  Project dashboard
3.  Dockerfile analyzer
4.  Terraform analyzer
5.  GitHub Actions workflow analyzer
6.  AI explanation layer
7.  History of analyses
8.  Downloadable report (Markdown)

## Phase 2

-   CloudWatch/ECS/Nginx/FastAPI log analysis
-   Incident timeline generation
-   Rule engine expansion
-   AI chat over analysis results

## Phase 3

-   AWS integration
-   Prometheus/Grafana monitoring
-   Team collaboration
-   Architecture visualization

## Functional Requirements

-   Upload supported files.
-   Parse files using dedicated parsers.
-   Run rule engine.
-   Produce findings with severity.
-   Send structured findings to AI provider.
-   Persist results.

## Non-functional Requirements

-   Dockerized deployment
-   REST API
-   PostgreSQL
-   CI/CD with GitHub Actions
-   Modular AI provider abstraction
-   Extensible parser architecture

## Proposed Tech Stack

-   Frontend: Next.js + TypeScript + Tailwind + shadcn/ui
-   Backend: FastAPI
-   ORM: SQLAlchemy + Alembic
-   Database: PostgreSQL
-   AI: Ollama / Gemini / Groq
-   Containers: Docker & Docker Compose
-   IaC: Terraform
-   Deployment: AWS ECS Fargate
-   Monitoring: Prometheus + Grafana

## Success Criteria

-   Analyze common DevOps artifacts accurately.
-   Explain findings clearly using AI.
-   Demonstrate enterprise-ready architecture in portfolio.
