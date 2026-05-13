# DevSentinel AI

AI-powered incident analysis for production codebases. Connect a repository, attach logs and stack traces, and trace failures to evidence-backed root causes, candidate patches, and sandbox validation results.

## Runtime Compatibility

| Component | Target (info.md) | Locally Verified (M1) |
| --------- | ----------------- | --------------------- |
| Node.js | 24.15.0 LTS | 22.19.0 |
| Python | 3.14.4 (3.13+ stable fallback) | 3.10.0 |
| pnpm | 11.0.6 | npm 10.x (compatible) |
| Next.js | 15.5.3 | 15.3.2 (build verified) |
| FastAPI | 0.136.1 | 0.115.12 (build verified) |

> **Next.js 15.3.2** is currently installed and production-build verified. The original target of 15.5.3 was not available in the npm registry at time of setup. Do not upgrade unless install and build are verified.

> **Python 3.10.0** is the local runtime. All dependencies install cleanly. When Python 3.13+ is available on the machine, upgrade and re-verify.

## Architecture

```
DevSentinel AI/
├── frontend/          Next.js 15.3.2 · React 19.1 · Tailwind CSS v4
├── backend/           FastAPI 0.115.12 · Python 3.10 · Pydantic v2.11
├── docker-compose.yml PostgreSQL 17 (pgvector 0.8.2) · Redis 8
├── .env.example       Shared environment variable template
├── info.md            Product specification
├── instructions.md    Engineering standards
└── design.md          UI/UX design system
```

### Frontend (`/frontend`)

| Layer | Technology |
| -------------- | ---------------------------------------------- |
| Framework | Next.js 15.3.2 (App Router, Turbopack dev) |
| UI | React 19.1, Tailwind CSS v4, Lucide icons |
| State | Zustand (UI), TanStack React Query (server) |
| Forms | React Hook Form + Zod |
| Code editor | Monaco Editor (future milestone) |
| Testing | Playwright (future milestone) |

### Backend (`/backend`)

| Layer | Technology |
| -------------- | ---------------------------------------------- |
| API framework | FastAPI 0.115.12 |
| Validation | Pydantic v2.11.3 |
| Database | PostgreSQL 17 + pgvector (via SQLAlchemy) |
| Cache / broker | Redis 8 |
| Background | Celery (future milestone) |
| AI | OpenAI API via LangGraph (future milestone) |
| Auth | Argon2 + JWT (future milestone) |

## Getting Started

### Prerequisites

- **Docker Desktop** (for PostgreSQL + Redis)
- **Node.js** >= 20 (target: 24 LTS)
- **npm** or **pnpm** (`npm install -g pnpm` for pnpm)
- **Python** >= 3.10 (target: 3.13+)

### 1. Clone and configure environment

```sh
cp .env.example .env
```

Edit `.env` to set `SECRET_KEY` and `OPENAI_API_KEY` (the API key is not required until AI milestones).

### 2. Start infrastructure

```sh
docker compose up -d
```

This starts:
- **PostgreSQL** on `localhost:5432` (user: `devsentinel`, password: `devsentinel_local`, db: `devsentinel`)
- **Redis** on `localhost:6379`

Verify health:
```sh
docker compose ps
```

### 3. Start the backend

```sh
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Run database migrations
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

- API root: http://localhost:8000
- Interactive docs: http://localhost:8000/api/v1/docs
- Health check: http://localhost:8000/api/v1/health

### Database Management

To create a new migration after changing models:
```sh
alembic revision --autogenerate -m "Description of changes"
```

To upgrade to the latest migration:
```sh
alembic upgrade head
```

To rollback one migration:
```sh
alembic downgrade -1
```

### 4. Start the frontend

```sh
cd frontend
npm install
npm run dev
```

- Landing page: http://localhost:3000
- Dashboard: http://localhost:3000/app

## API Error Format

Every error response follows this exact shape:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Repository 'repo_abc' was not found.",
    "requestId": "req_a1b2c3d4e5f6g7h8i9j0k1l2",
    "retryable": false,
    "details": {}
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `error.code` | `string` | Machine-readable error code (e.g. `NOT_FOUND`, `RATE_LIMITED`) |
| `error.message` | `string` | Human-readable explanation |
| `error.requestId` | `string` | Correlates to `X-Request-ID` response header |
| `error.retryable` | `boolean` | Whether the client should retry the request |
| `error.details` | `object` | Additional context (validation errors, affected fields) |

## Health Endpoint

```
GET /api/v1/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-05-11T18:30:00+00:00",
  "requestId": "req_a1b2c3d4e5f6g7h8i9j0k1l2"
}
```

## Current Status (Milestone 2)

### Implemented

- Monorepo structure (frontend + backend + docker-compose)
- Docker Compose for PostgreSQL 17 (pgvector 0.8.2) and Redis 8
- FastAPI backend with application factory pattern
- Health endpoint with `requestId` in body
- Typed API error hierarchy (404, 409, 403, 401, 422, 429, 500)
- Error envelope: `{"error": {"code", "message", "requestId", "retryable", "details"}}`
- Request ID middleware (generates `req_*` IDs, logs method/path/status/duration)
- Structured logging to stdout with ISO timestamps
- CORS configuration for frontend origin
- Next.js 15.3.2 frontend with App Router
- Full design token system from design.md (dark-mode-first)
- Inter + JetBrains Mono font loading
- App shell: sidebar with active-state navigation + top bar with dynamic breadcrumbs
- Landing page with product preview, feature grid, and trust section
- Dashboard overview with metric cards, empty states, and system health panel
- Shared `.env.example` with configurable AI model names and runtime documentation
- SQLAlchemy async database engine and declarative base
- PostgreSQL-ready schema mapping all core domain concepts (Workspaces, Repositories, Incidents, Analysis Runs)
- UUID primary keys, timestamp mixins, and robust foreign keys
- Alembic migration environment initialized
- Repository and service layer foundation

### Intentionally Deferred

- Authentication (JWT, sessions, GitHub OAuth)
- Repository import and code indexing
- Tree-sitter semantic parsing
- Celery background workers
- AI workflows (LangGraph + OpenAI)
- Incident CRUD and analysis
- Patch generation and diff viewer
- Sandbox execution
- Real-time SSE streaming
- Command menu (⌘K)
- E2E and integration tests
- Production deployment configuration

## License

Private — portfolio project.
