# OpsPilot Architecture

## Architecture Style

-   Modular Monolith (FastAPI backend)
-   Next.js frontend
-   PostgreSQL database
-   AI Provider abstraction

## Request Flow

Client -\> Next.js -\> FastAPI -\> Analyzer Engine -\> Rule Engine -\>
AI Provider -\> PostgreSQL -\> Response

## Core Modules

-   auth
-   projects
-   analyzers
-   parsers
-   providers
-   reports
-   core

## Principles

-   Clear module boundaries
-   Dependency Injection
-   Rule-based analysis first, AI explanations second
-   Easy future extraction into microservices
