# SmokeTest App

A full-stack task management application designed as a **smoke test repository for [AgentFlow](https://github.com/The-AgenticFlow/AgentFlow)**.

This repo exercises every agent in the AgentFlow pipeline:

| Agent | Scenario | Issue Labels |
|-------|----------|-------------|
| **NEXUS** | Issue triage, CI-first routing, flow recovery | `ci`, `priority:high` |
| **FORGE** | Feature implementation, bug fixes, security patches | `feature`, `bug`, `security` |
| **SENTINEL** | Code review, spec verification, security audit | All PRs |
| **VESSEL** | CI polling, merge gating, conflict resolution | All PRs |
| **LORE** | ADRs, changelog, API docs | `documentation` |

## Stack

### Backend (Python)
- **FastAPI** — async REST API
- **SQLAlchemy** — ORM with SQLite (dev) / PostgreSQL (prod)
- **Redis** — caching and rate limiting
- **Alembic** — database migrations
- **pytest** — test suite

### Frontend (TypeScript)
- **React 18** — UI
- **Vite** — build tool
- **Zustand** — state management
- **Vitest** + **Testing Library** — test suite

## Quick Start

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Project Structure

```
smoketest-app/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── routes.py        # API endpoints
│   │   ├── auth.py          # Authentication (incomplete — for bugfix issue)
│   │   ├── cache.py         # Redis caching (stub — for feature issue)
│   │   └── config.py        # Settings
│   ├── tests/
│   │   ├── test_routes.py
│   │   ├── test_auth.py     # Tests documenting bugs — for bugfix issue
│   │   └── conftest.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── store.ts         # Zustand store (has bug — for bugfix issue)
│   │   ├── api.ts           # API client
│   │   └── components/      # Empty — for feature issue
│   ├── tests/
│   │   ├── App.test.tsx
│   │   └── setup.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
└── docs/
    └── api.md              # API docs (incomplete — for docs issue)
```
