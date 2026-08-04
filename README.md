# OpsPilot

> AI-assisted DevOps Operations Platform

## Overview

OpsPilot helps DevOps engineers and SREs analyze infrastructure, CI/CD
pipelines, and production logs. It combines deterministic rule-based
analysis with AI explanations to provide actionable recommendations.

## Objectives

-   Analyze Dockerfiles
-   Analyze Terraform configurations
-   Analyze GitHub Actions workflows
-   Analyze application and infrastructure logs
-   Generate AI-powered explanations
-   Produce downloadable reports

## Tech Stack

-   Frontend: Next.js + TypeScript + Tailwind CSS + shadcn/ui
-   Backend: FastAPI
-   Database: PostgreSQL
-   ORM: SQLAlchemy + Alembic
-   AI Providers: Gemini, Groq, Ollama (pluggable)
-   Docker & Docker Compose
-   GitHub Actions
-   Terraform
-   AWS ECS Fargate (future)

## Repository Structure

See `PROJECT_STRUCTURE.md`.

## Development Workflow

1.  Read the documentation first.
2.  Follow `ARCHITECTURE.md`.
3.  Keep parser, rule engine and AI provider separate.
4.  Write tests for new analyzers.
5.  Keep commits focused.

## Documentation

-   PRD.md
-   ARCHITECTURE.md
-   TECH_STACK.md
-   PROJECT_STRUCTURE.md
-   DATABASE.md
-   API_SPEC.md
-   ANALYZER_ENGINE.md
-   CODING_STANDARDS.md

## Milestone 1

-   [ ] Project scaffolding
-   [ ] Authentication
-   [ ] Database models
-   [ ] Docker analyzer
-   [ ] Terraform analyzer
-   [ ] GitHub Actions analyzer

## Engineering Principles

-   Modular monolith
-   Clean Architecture
-   SOLID
-   Dependency Injection
-   Rule-based analysis first
-   AI explains findings; it does not generate them.

## Run

``` bash
docker compose up --build
```

## Vision

Build a production-ready DevOps assistant with pluggable analyzers and
AI providers.
