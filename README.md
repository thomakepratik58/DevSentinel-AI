# DevSentinel AI

AI-powered incident analysis for production codebases. Connect a repository, attach logs and stack traces, and trace failures to evidence-backed root causes, candidate patches, and sandbox validation results.

## Architecture

```
DevSentinel AI/
├── frontend/          Next.js 15 · React 19 · Tailwind CSS v4
├── backend/           FastAPI · Python 3.10+ · Pydantic v2
├── docker-compose.yml PostgreSQL 17 (pgvector) · Redis 8
├── .env.example       Shared environment variable template
└── docs/              info.md · instructions.md · design.md
```

### Frontend (`/frontend`)

| Layer          | Technology                                     |
| -------------- | ---------------------------------------------- |
| Framework      | Next.js 15 (App Router)                        |
| UI             | React 19, Tailwind CSS v4, Lucide icons        |
| State          | Zustand (UI), TanStack React Query (server)    |
| Forms          | React Hook Form + Zod                          |
| Code editor    | Monaco Editor (future milestone)               |
| Testing        | Playwright (future milestone)                  |

### Backend (`/backend`)

| Layer          | Technology                                     |
| -------------- | ---------------------------------------------- |
| API framework  | FastAPI 0.115                                  |
| Validation     | Pydantic v2                                    |
| Database       | PostgreSQL 17 + pgvector (via SQLAlchemy)      |
| Cache / broker | Redis 8                                        |
| Background     | Celery (future milestone)                      |
| AI             | OpenAI API via LangGraph (future milestone)    |
| Auth           | Argon2 + JWT (future milestone)                |

## Getting Started

### Prerequisites

- **Docker Desktop** (for PostgreSQL + Redis)
- **Node.js** >= 20 (24 LTS recommended)
- **pnpm** >= 9 (`npm install -g pnpm`)
- **Python** >= 3.10

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
uvicorn app.main:app --reload --port 8000
```

- API root: http://localhost:8000
- Interactive docs: http://localhost:8000/api/v1/docs
- Health check: http://localhost:8000/api/v1/health

### 4. Start the frontend

```sh
cd frontend
pnpm install
pnpm run dev
```

- App: http://localhost:3000
- Dashboard: http://localhost:3000/app

## API Error Format

Every error response follows this shape:

```json
{
  "error_code": "NOT_FOUND",
  "message": "Repository 'repo_abc' was not found.",
  "details": null,
  "trace_id": "req_a1b2c3d4e5f6g7h8i9j0k1l2"
}
```

The `trace_id` correlates to the `X-Request-ID` response header for debugging.

## Current Status (Milestone 1)

### Implemented

- Monorepo structure (frontend + backend)
- Docker Compose for PostgreSQL (pgvector) and Redis
- FastAPI backend with application factory pattern
- Health endpoint (`GET /api/v1/health`)
- Typed API error hierarchy (404, 409, 403, 401, 422, 429, 500)
- Request ID middleware (generates `req_*` IDs, logs method/path/status/duration)
- Structured logging to stdout
- CORS configuration for frontend origin
- Next.js 15 frontend with App Router
- Full design token system from design.md (dark-mode-first)
- Inter + JetBrains Mono font loading
- App shell: sidebar with active-state navigation + top bar with breadcrumbs
- Landing page with product preview, feature grid, and trust section
- Dashboard overview with metric cards, empty states, and system health panel
- Shared `.env.example` with configurable AI model names

### Intentionally Deferred

- Authentication (JWT, sessions, GitHub OAuth)
- Database schema and migrations (SQLAlchemy + Alembic)
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
