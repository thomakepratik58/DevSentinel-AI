# DevSentinel AI - Single Source of Truth

**Document version:** 1.0.0  
**Last updated:** 2026-05-11  
**Project codename:** DevSentinel AI  
**Primary goal:** Build a production-grade, full-stack AI codebase debugging and incident resolution platform that demonstrates advanced Python backend engineering, modern web development, AI orchestration, secure systems design, and interview-ready architectural depth.

## Instructions for AI Assistant:
- Read this ENTIRE document before generating ANY code
- Follow ALL specifications exactly as written
- Ask for clarification if ANY requirement is ambiguous
- Generate complete, production-ready code (no placeholders)
- Include error handling for ALL edge cases mentioned
- Implement ALL security measures specified
- Follow the exact tech stack and versions listed
- Adhere to coding standards and conventions defined
- Reference this document when making architectural decisions

> Important: This file is the canonical product, architecture, UI, API, security, database, AI, testing, and deployment specification. Do not invent alternate libraries, folder structures, endpoint names, schema names, auth behavior, or UI patterns unless this document explicitly allows it.

---

## Table of Contents

1. [Project Overview and Context](#1-project-overview-and-context)
2. [Tech Stack](#2-tech-stack)
3. [Core Feature Set](#3-core-feature-set)
4. [System Architecture](#4-system-architecture)
5. [Database Design](#5-database-design)
6. [AI Workflow](#6-ai-workflow)
7. [Security Implementation](#7-security-implementation)
8. [API Specifications](#8-api-specifications)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment Pipeline](#10-deployment-pipeline)
11. [Code Standards and Conventions](#11-code-standards-and-conventions)
12. [Limitations and Constraints](#12-limitations-and-constraints)
13. [Future Roadmap](#13-future-roadmap)
14. [Implementation Checklist](#14-implementation-checklist)

---

# 1. Project Overview and Context

## 1.1 Problem Statement

Modern software teams lose significant engineering time debugging production errors because incident context is scattered across stack traces, logs, GitHub issues, documentation, tests, and source code. General AI chatbots can explain isolated snippets but usually fail to reliably connect a production incident to the exact repository files, historical changes, failing tests, and safe remediation steps.

DevSentinel AI solves this by providing an AI-powered developer platform that ingests a repository, builds a searchable code intelligence layer, accepts bug reports or stack traces, retrieves relevant files and symbols, produces root-cause analysis, generates a safe patch proposal, runs tests in a sandbox, and presents the entire reasoning chain through a polished real-time web dashboard.

## 1.2 Solution Approach

The application uses:

- A Python FastAPI backend for authenticated APIs, repository ingestion, incident orchestration, background jobs, and WebSocket/SSE streaming.
- PostgreSQL 18 with pgvector for relational data plus vector search over code chunks.
- Redis for caching, job broker state, distributed locks, and rate limiting.
- Celery workers for long-running repository indexing, embeddings generation, AI analysis, patch generation, and sandbox test execution.
- LangGraph for deterministic multi-step AI workflows.
- OpenAI API models for code reasoning, structured output, and embeddings.
- Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui for a production-grade developer dashboard.

## 1.3 Target Users

| User Type | Need | Primary Screens |
|---|---|---|
| Python developer candidate | Showcase full-stack, AI, backend, DevOps, and architecture skills | All screens |
| Engineering lead | Understand whether AI diagnosis is grounded and safe | Incident detail, patch diff, risk panel |
| Backend developer | Diagnose API bugs quickly | Repository explorer, AI analysis, logs |
| Full-stack developer | Trace frontend-to-backend incidents | Incident timeline, code citations |
| SRE/DevOps engineer | Review incident metadata, test output, runtime logs | Sandbox runs, audit events, observability dashboard |

## 1.4 Core Use Cases

1. User creates an account and workspace.
2. User imports a public GitHub repository or uploads a repository archive.
3. System indexes source files, docs, tests, dependency manifests, and symbols.
4. User submits an incident with title, stack trace, logs, expected behavior, actual behavior, severity, and affected environment.
5. AI workflow retrieves relevant code chunks, docs, and tests.
6. AI explains root cause with code citations.
7. AI proposes a patch set as unified diffs.
8. System validates the patch format and optionally applies it in a sandbox copy.
9. System runs configured tests in a locked-down sandbox.
10. User reviews patch, test output, confidence score, and risk analysis.
11. User exports report or opens a pull request.

## 1.5 Success Metrics and KPIs

| KPI | Target | Measurement |
|---|---:|---|
| Repository indexing completion rate | >= 95% for supported repositories | `repositories.index_status` and worker logs |
| AI analysis completion rate | >= 90% without manual retry | `agent_runs.status` |
| Grounded answer citation coverage | >= 85% of root-cause claims cite code chunks | Count `retrieval_results` used in final answer |
| Patch validation success rate | >= 80% for generated patches | `patch_sets.validation_status` |
| Sandbox test execution success rate | >= 75% when repo has valid test config | `sandbox_runs.status` |
| P95 incident analysis time | <= 120 seconds for repos under 10k files | OpenTelemetry spans |
| P95 API response time | <= 300 ms for non-AI endpoints | API metrics |
| Lighthouse performance score | >= 90 desktop, >= 80 mobile | CI Lighthouse run |
| Security scan critical findings | 0 | CI security job |

## 1.6 Scope

### In Scope

- Email/password auth and GitHub OAuth login.
- Workspace and member roles.
- Public GitHub repository import by URL.
- Repository ZIP upload for local/demo use.
- Python and TypeScript/JavaScript code indexing.
- Markdown documentation indexing.
- Function/class/symbol extraction using Tree-sitter where supported.
- Vector and keyword hybrid search.
- Incident submission and AI analysis.
- Patch generation with diff viewer.
- Sandbox test run simulation and optional Docker-based execution.
- Real-time workflow progress updates.
- Audit logging.
- Production-ready deployment configuration.

### Out of Scope for v1

- Enterprise SSO/SAML.
- Private GitHub App installation flow.
- Multi-region deployment.
- Fine-tuned custom models.
- Automatic production deployment of generated patches.
- Arbitrary shell access from the UI.
- Running untrusted code outside hardened containers.
- Support for every language ecosystem.

---

# 2. Tech Stack

## 2.1 Version Lock Policy

- All versions below are fixed for implementation.
- Use exact versions in `package.json`, `pyproject.toml`, Dockerfiles, and CI.
- Do not use `latest`, loose semver ranges, or unpinned base images.
- Only update versions through an explicit dependency upgrade task.

## 2.2 Frontend Stack

| Category | Package/Tool | Version | Justification |
|---|---|---:|---|
| Runtime | Node.js | 24.15.0 LTS | Stable LTS runtime for production Next.js builds. |
| Package manager | pnpm | 11.0.6 | Fast installs, deterministic lockfile, workspace support. |
| Framework | Next.js | 15.5.3 | App Router, server components, server actions, route handlers, optimized bundling. |
| UI library | React | 19.2.0 | Modern component model and concurrent rendering support. |
| Language | TypeScript | 5.8.3 | Strong typing, better DX, safer API contracts. |
| Styling | Tailwind CSS | 4.1.12 | Utility-first pixel-perfect dashboard styling. |
| Component system | shadcn CLI | 3.2.1 | Copy-owned accessible components, not black-box UI dependency. |
| Primitives | radix-ui | 1.4.3 | Accessible base primitives used by shadcn new-york style. |
| Icons | lucide-react | 1.14.0 | Lightweight consistent icon system. |
| Forms | react-hook-form | 7.75.0 | Performant form state handling. |
| Validation | zod | 4.4.3 | Shared frontend schema validation. |
| Client state | zustand | 5.0.13 | Lightweight local UI state store. |
| Server state | @tanstack/react-query | 5.76.1 | Data fetching, caching, retries, optimistic updates. |
| Code editor | monaco-editor | 0.56.0 | Rich file viewer and diff editor base. |
| React Monaco wrapper | @monaco-editor/react | 4.7.0 | React integration for Monaco. |
| Charts | recharts | 2.15.4 | Dashboard metrics, simple charts. |
| E2E testing | @playwright/test | 1.52.0 | Cross-browser testing. |

## 2.3 Backend Stack

| Category | Package/Tool | Version | Justification |
|---|---|---:|---|
| Runtime | Python | 3.14.4 | Modern Python runtime with improved async introspection and performance. |
| API framework | FastAPI | 0.136.1 | Type-hint driven APIs, OpenAPI generation, async support. |
| ASGI server | Uvicorn | 0.41.0 | Production ASGI server for FastAPI. |
| Data validation | Pydantic | 2.13.4 | Runtime validation and schema generation. |
| ORM | SQLAlchemy | 2.0.49 | Typed ORM and SQL Core support. |
| Migrations | Alembic | 1.18.4 | Database migration standard for SQLAlchemy. |
| PostgreSQL driver | psycopg | 3.2.9 | Modern PostgreSQL driver. |
| Background jobs | Celery | 5.6.3 | Mature distributed task queue. |
| Redis client | redis-py | 5.2.1 | Redis cache, broker, locks, rate limits. |
| HTTP client | httpx | 0.28.1 | Async outbound HTTP calls. |
| Git integration | GitPython | 3.1.49 | Repository cloning and local analysis. |
| Password hashing | argon2-cffi | 23.1.0 | Secure password hashing. |
| JWT | PyJWT | 2.10.1 | JWT access tokens. |
| Testing | pytest | 9.0.3 | Unit and integration tests. |
| Async tests | pytest-asyncio | 0.26.0 | Async FastAPI tests. |
| Coverage | coverage | 7.8.0 | Coverage reporting. |
| Formatting | ruff | 0.11.8 | Fast linting and formatting. |
| Typing | mypy | 1.15.0 | Static type checking. |

## 2.4 Database and Storage

| Category | Tool | Version | Justification |
|---|---|---:|---|
| Relational DB | PostgreSQL | 18.3 | Strong relational modeling, JSONB, full-text search, reliability. |
| Vector extension | pgvector | 0.8.2 | Vector similarity search inside PostgreSQL. |
| DB Docker image | pgvector/pgvector | 0.8.2-pg18 | PostgreSQL 18 with pgvector preinstalled. |
| Cache/broker | Redis | 8.0.x | Rate limiting, job queue broker, cache, locks. |
| Object storage local | MinIO | RELEASE.2026-04-22T22-12-26Z | S3-compatible local storage for uploads and artifacts. |
| Production object storage | AWS S3 compatible | API 2006-03-01 | Portable artifact storage. |

## 2.5 AI/ML Stack

| Category | Tool/Model | Version/Name | Justification |
|---|---|---|---|
| AI workflow engine | LangGraph | 1.1.10 | Stateful graph-based agent orchestration. |
| LLM provider | OpenAI Responses API | v1 | Tool calling, structured outputs, streaming. |
| Main reasoning model | gpt-5.2 | API model alias | Best for coding and agentic reasoning tasks. |
| Fast/cost model | gpt-5-mini | API model alias | Used for summaries, classification, and lower-risk steps. |
| Embedding model | text-embedding-3-large | 3072 dimensions | High-quality code and text retrieval. |
| Optional cheaper embedding model | text-embedding-3-small | 1536 dimensions | Local/dev cost control. |
| Structured output validation | Pydantic | 2.13.4 | Validate AI JSON outputs before persistence. |
| Reranking | LLM-based rerank | gpt-5-mini | Reorders retrieved chunks for context assembly. |

## 2.6 DevOps, Monitoring, and Security Tools

| Category | Tool | Version | Purpose |
|---|---|---:|---|
| Containers | Docker | 26.x | Local and production containerization. |
| Compose | Docker Compose | 5.1.3 | Local multi-service environment. |
| CI/CD | GitHub Actions | pinned action SHAs | Build, test, scan, deploy. |
| Backend deploy | Fly.io or Render | N/A | Simple deploy target for portfolio demo. |
| Frontend deploy | Vercel | N/A | Next.js optimized hosting. |
| Observability | OpenTelemetry | 1.33.x | Traces, metrics, logs correlation. |
| Error tracking | Sentry | 2.x SDKs | Frontend/backend error reporting. |
| Security scanning | pip-audit, npm audit, Trivy | pinned in CI | Dependency and image scanning. |
| Secrets | Doppler or platform secrets | N/A | Environment secret management. |

---

# 3. Core Feature Set

## 3.1 Feature: Authentication and Workspace Onboarding

### User Flow

1. User lands on `/` and clicks `Start debugging`.
2. User signs up with email/password or GitHub OAuth.
3. User verifies email in dev via console token and in prod via email provider.
4. System creates a default workspace.
5. User is redirected to `/app`.
6. User sees empty state prompting repository import.

### API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Create user and default workspace |
| POST | `/api/v1/auth/login` | Authenticate email/password |
| POST | `/api/v1/auth/logout` | Revoke refresh token |
| POST | `/api/v1/auth/refresh` | Rotate refresh token and issue access token |
| GET | `/api/v1/auth/me` | Return current user and workspace memberships |
| GET | `/api/v1/auth/github/start` | Start OAuth flow |
| GET | `/api/v1/auth/github/callback` | Complete OAuth flow |

### Request/Response Example

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "dev@example.com",
  "password": "CorrectHorseBatteryStaple!42",
  "full_name": "Avery Developer"
}
```

```json
{
  "user": {
    "id": "usr_01JZ0000000000000000000000",
    "email": "dev@example.com",
    "full_name": "Avery Developer"
  },
  "workspace": {
    "id": "wsp_01JZ0000000000000000000000",
    "name": "Avery's Workspace"
  },
  "access_token": "jwt-access-token",
  "expires_in": 900
}
```

### Database Interactions

- Insert `users` row.
- Insert `workspaces` row.
- Insert `workspace_members` row with role `owner`.
- Insert hashed refresh token into `refresh_tokens`.
- Insert `audit_events` row with action `auth.register`.

### UI Components

- `AuthLayout`
- `RegisterForm`
- `LoginForm`
- `OAuthButton`
- `PasswordStrengthMeter`
- `FormErrorBanner`

### Errors and Edge Cases

| Scenario | Behavior |
|---|---|
| Email already exists | Return `409 EMAIL_ALREADY_EXISTS` |
| Weak password | Return `422 WEAK_PASSWORD` with rules |
| OAuth email already registered | Link provider to existing account after verified OAuth email |
| Refresh token reuse | Revoke all user tokens and require login |
| More than 5 failed login attempts in 15 minutes | Return `429 LOGIN_RATE_LIMITED` |

## 3.2 Feature: Repository Import

### User Flow

1. User clicks `Import repository`.
2. User selects `GitHub URL` or `ZIP upload`.
3. User submits repository URL or file.
4. Backend creates repository record with `index_status=queued`.
5. Celery job clones or extracts repository.
6. Worker scans files and creates file records.
7. Worker chunks code and schedules embedding jobs.
8. UI shows live indexing progress.
9. Repository becomes searchable when status is `ready`.

### API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/repositories` | Import GitHub repo by URL |
| POST | `/api/v1/repositories/upload` | Upload repo ZIP |
| GET | `/api/v1/repositories` | List workspace repos |
| GET | `/api/v1/repositories/{repository_id}` | Repository details |
| DELETE | `/api/v1/repositories/{repository_id}` | Soft-delete repository |
| POST | `/api/v1/repositories/{repository_id}/reindex` | Queue reindex |
| GET | `/api/v1/repositories/{repository_id}/files` | Browse indexed files |
| GET | `/api/v1/repositories/{repository_id}/files/{file_id}` | Read file content |

### Request Example

```json
{
  "workspace_id": "wsp_01JZ0000000000000000000000",
  "provider": "github_public_url",
  "url": "https://github.com/example/demo-api",
  "default_branch": "main"
}
```

### Database Interactions

- Insert into `repositories`.
- Insert into `repository_import_jobs`.
- Worker inserts into `repository_files`, `code_symbols`, `code_chunks`, `chunk_embeddings`.
- Update `repositories.index_status` as `queued`, `cloning`, `scanning`, `embedding`, `ready`, or `failed`.

### UI Components

- `RepositoryImportDialog`
- `RepoUrlInput`
- `RepoUploadDropzone`
- `IndexingProgressCard`
- `RepositoryList`
- `RepositoryEmptyState`

### Validation Rules

- GitHub URL must match `^https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$`.
- ZIP upload max size is 50 MB in local/demo mode.
- Block nested `.git`, `node_modules`, `.venv`, `dist`, `build`, `.next`, `.cache`, binary files, secrets files.
- Max indexed files per repository in v1: 10,000.
- Max single file size for indexing: 512 KB.
- Store SHA-256 hash of file content.

## 3.3 Feature: Code Intelligence Indexing

### User Flow

This feature is mostly background-driven.

1. Repository import queues `index_repository_task`.
2. Worker scans file tree.
3. Worker filters unsupported/unsafe files.
4. Worker extracts language, path, size, hash.
5. Worker extracts symbols for Python and TypeScript/JavaScript.
6. Worker chunks files by semantic boundaries.
7. Worker creates embeddings in batches.
8. Worker writes vector rows and full-text search rows.

### Chunking Rules

| File Type | Strategy |
|---|---|
| Python | Function/class-aware chunks; fallback to 160 lines with 30-line overlap |
| TypeScript/JavaScript | Export/function/component-aware chunks; fallback to 160 lines with 30-line overlap |
| Markdown | Heading-aware chunks; fallback to 900 tokens with 150-token overlap |
| JSON/YAML | Top-level key chunks; fallback to 300 lines |
| Test files | Mark with `is_test=true` and preserve test names |

### Database Interactions

- Upsert `repository_files` by `(repository_id, path)`.
- Delete old chunks for changed files.
- Insert new chunks.
- Insert embedding vector with dimension 3072.
- Build/update HNSW indexes after bulk inserts.

### Errors and Edge Cases

| Scenario | Handling |
|---|---|
| File contains invalid UTF-8 | Decode with replacement and mark `decode_warnings` |
| Embedding API rate limit | Exponential backoff with jitter, max 5 retries |
| Repository too large | Mark `partial_index=true`; index highest-value files first |
| Parse failure | Store raw chunk fallback and parser error in metadata |
| Duplicate file content | De-duplicate embeddings by content hash within repo |

## 3.4 Feature: Incident Submission and AI Analysis

### User Flow

1. User opens a repository and clicks `New incident`.
2. User enters title, severity, environment, expected behavior, actual behavior, stack trace, logs, and optional reproduction steps.
3. System creates incident with status `draft` or `queued`.
4. User clicks `Run AI analysis`.
5. Backend creates `agent_run` and queues workflow task.
6. UI streams agent steps in real time.
7. System displays root cause, cited files, confidence, and recommended actions.

### API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/incidents` | Create incident |
| GET | `/api/v1/incidents` | List incidents |
| GET | `/api/v1/incidents/{incident_id}` | Incident details |
| PATCH | `/api/v1/incidents/{incident_id}` | Update incident fields |
| POST | `/api/v1/incidents/{incident_id}/analyze` | Start AI analysis |
| GET | `/api/v1/incidents/{incident_id}/runs` | List AI runs |
| GET | `/api/v1/agent-runs/{run_id}` | Read AI run details |
| GET | `/api/v1/agent-runs/{run_id}/events` | SSE stream of run events |

### Request Example

```json
{
  "repository_id": "repo_01JZ0000000000000000000000",
  "title": "Login returns 500 after token expiry",
  "severity": "high",
  "environment": "production",
  "expected_behavior": "Expired tokens should return 401 and prompt re-login.",
  "actual_behavior": "API returns 500 with AttributeError.",
  "stack_trace": "AttributeError: 'NoneType' object has no attribute 'id' at app/auth/service.py:88",
  "logs": "2026-05-11T09:04:22Z ERROR request_id=...",
  "reproduction_steps": [
    "Login with valid credentials",
    "Wait until token expires",
    "Call GET /api/me"
  ]
}
```

### UI Components

- `IncidentCreatePage`
- `IncidentForm`
- `SeveritySelect`
- `StackTraceEditor`
- `AgentTimeline`
- `RootCausePanel`
- `CodeCitationList`
- `ConfidenceBadge`
- `RiskSummaryCard`

### Edge Cases

- Incident cannot be analyzed until repository index status is `ready` or `partial_ready`.
- Analysis is idempotent per run. Retrying creates a new run and links to prior runs.
- If logs exceed 200 KB, truncate middle and preserve head/tail.
- If no relevant chunks found, workflow must ask user for more context rather than hallucinating.

## 3.5 Feature: Patch Generation and Diff Review

### User Flow

1. User reviews AI root cause.
2. User clicks `Generate patch`.
3. AI creates a unified diff only for relevant files.
4. Backend validates patch format.
5. UI displays file-by-file diff.
6. User can accept, reject, or request revision.

### API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/incidents/{incident_id}/patches` | Generate patch |
| GET | `/api/v1/patches/{patch_id}` | Read patch set |
| POST | `/api/v1/patches/{patch_id}/validate` | Validate diff syntax |
| POST | `/api/v1/patches/{patch_id}/revise` | Request patch revision |
| POST | `/api/v1/patches/{patch_id}/export` | Export patch file |

### Patch Rules

- Patch must be unified diff format.
- Patch must only touch files retrieved or explicitly justified by AI.
- Patch must not modify secrets, lockfiles, generated files, or binary files unless explicitly allowed.
- Patch must include tests when feasible.
- Patch must include rationale per file.

### UI Components

- `PatchGenerationButton`
- `PatchDiffViewer`
- `FileChangeTabs`
- `PatchRationalePanel`
- `PatchValidationStatus`
- `RevisionPromptBox`

## 3.6 Feature: Sandbox Test Execution

### User Flow

1. User clicks `Run tests` from patch page.
2. Backend creates sandbox run.
3. Worker creates isolated working copy.
4. Worker applies patch.
5. Worker runs detected test command.
6. UI streams logs.
7. System stores exit code, duration, output, and summary.

### API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/patches/{patch_id}/sandbox-runs` | Start sandbox run |
| GET | `/api/v1/sandbox-runs/{sandbox_run_id}` | Read run details |
| GET | `/api/v1/sandbox-runs/{sandbox_run_id}/events` | SSE stream logs |
| POST | `/api/v1/sandbox-runs/{sandbox_run_id}/cancel` | Cancel run |

### Test Command Detection

| Repo Signal | Command |
|---|---|
| `pyproject.toml` with pytest | `pytest -q` |
| `requirements.txt` and `tests/` | `python -m pytest -q` |
| `package.json` with test script | `pnpm test -- --runInBand` |
| no test config | return `no_test_command_detected` |

### Sandbox Security Rules

- Run container as non-root.
- Disable privileged mode.
- No host mounts except ephemeral temp dir.
- Network disabled by default after dependencies are installed.
- CPU limit: 2 cores.
- Memory limit: 2 GB.
- Timeout: 180 seconds.
- Kill process tree on timeout.

## 3.7 Feature: Real-Time Developer Dashboard

### Pages

| Route | Purpose |
|---|---|
| `/` | Marketing/landing page |
| `/login` | Login |
| `/register` | Register |
| `/app` | Dashboard home |
| `/app/repositories` | Repository list |
| `/app/repositories/[id]` | Repository detail |
| `/app/repositories/[id]/files` | File explorer |
| `/app/incidents` | Incident list |
| `/app/incidents/new` | New incident |
| `/app/incidents/[id]` | Incident detail, agent timeline, analysis |
| `/app/patches/[id]` | Patch diff and sandbox results |
| `/app/settings` | Workspace/user settings |

### Pixel-Perfect UI Requirements

- Use a dark developer-console aesthetic by default.
- Base background: `#09090B`.
- Card background: `#111113`.
- Border: `#27272A`.
- Primary accent: `#8B5CF6`.
- Success: `#22C55E`.
- Warning: `#F59E0B`.
- Error: `#EF4444`.
- Font: `Inter` for UI, `JetBrains Mono` for code.
- Radius: `16px` for cards, `10px` for controls.
- Spacing scale: 4 px base, use Tailwind spacing consistently.
- Minimum tap target: 44 x 44 px.
- All interactive elements require focus-visible ring.
- Skeleton loading state required for every data-heavy page.
- Empty states must include icon, explanation, and CTA.
- Error states must include message, retry action, and support trace id.

---

# 4. System Architecture

## 4.1 High-Level Component Diagram

```mermaid
flowchart LR
    U[User Browser] --> FE[Next.js Frontend]
    FE --> API[FastAPI API]
    FE --> SSE[SSE Event Streams]
    API --> PG[(PostgreSQL 18 + pgvector)]
    API --> R[(Redis)]
    API --> OBJ[(S3/MinIO Object Storage)]
    API --> Q[Celery Queue]
    Q --> W1[Indexing Worker]
    Q --> W2[AI Workflow Worker]
    Q --> W3[Sandbox Worker]
    W1 --> PG
    W1 --> AI[OpenAI API]
    W2 --> PG
    W2 --> AI
    W3 --> Docker[Isolated Docker Sandbox]
    W3 --> PG
    API --> OTEL[OpenTelemetry Collector]
    FE --> Sentry[Sentry]
    API --> Sentry
```

## 4.2 Service Responsibilities

| Service | Responsibilities |
|---|---|
| Next.js frontend | Auth UI, dashboard, forms, file explorer, diff viewer, real-time progress, UX polish |
| FastAPI API | Auth, RBAC, REST API, validation, SSE, job creation, database transactions |
| PostgreSQL + pgvector | Primary relational data, embeddings, full-text search, audit log |
| Redis | Rate limits, Celery broker, short-lived cache, distributed locks |
| Celery workers | Repository indexing, embeddings, AI analysis, patch generation, sandbox execution |
| Object storage | Uploaded ZIP files, exported patch files, sandbox artifacts |
| OpenAI API | Reasoning, structured output, embeddings |
| OpenTelemetry | Trace and metric collection |

## 4.3 Request/Response Lifecycle

Example: `POST /api/v1/incidents/{id}/analyze`

1. Frontend sends request with `Authorization: Bearer <access_token>`.
2. FastAPI validates JWT and loads user.
3. RBAC middleware verifies user can access incident workspace.
4. API validates incident is linked to a ready repository.
5. API creates `agent_runs` row in one transaction.
6. API queues `run_incident_analysis_task` in Celery.
7. API returns `202 Accepted` with `run_id` and SSE URL.
8. Frontend subscribes to `/api/v1/agent-runs/{run_id}/events`.
9. Worker updates `agent_steps`; events are published through Redis pub/sub.
10. SSE endpoint streams events to frontend.
11. Worker persists final result and marks run `succeeded` or `failed`.
12. Frontend invalidates query cache and renders result.

## 4.4 Caching Strategy

| Data | Cache Location | TTL | Invalidation |
|---|---|---:|---|
| Current user profile | React Query | 5 min | logout, profile update |
| Repository list | React Query | 60 sec | import/delete/reindex |
| File tree | Redis + React Query | 10 min | repository reindex |
| File content | Redis | 30 min | file hash change |
| Retrieval results | PostgreSQL | permanent per run | not mutated |
| Rate limit counters | Redis | sliding window | TTL expiration |
| SSE event backlog | Redis streams | 1 hour | stream trimming |

## 4.5 Rate Limiting

| Scope | Limit | Window | Error Code |
|---|---:|---:|---|
| Login attempts per IP+email | 5 | 15 min | `LOGIN_RATE_LIMITED` |
| Registration per IP | 3 | 1 hour | `REGISTER_RATE_LIMITED` |
| Repository imports per user | 5 | 1 hour | `REPO_IMPORT_RATE_LIMITED` |
| AI analyses per workspace | 20 | 24 hours | `AI_DAILY_LIMIT_REACHED` |
| Patch generations per incident | 5 | 24 hours | `PATCH_LIMIT_REACHED` |
| Sandbox runs per patch | 3 | 24 hours | `SANDBOX_LIMIT_REACHED` |
| General API per user | 300 | 1 min | `API_RATE_LIMITED` |

## 4.6 Scalability Considerations

- API service is stateless and horizontally scalable.
- Use Redis distributed locks for repository indexing to avoid duplicate work.
- Use Celery queues by workload: `indexing`, `ai`, `sandbox`, `default`.
- Embedding generation uses batch size 64 chunks with backoff.
- PostgreSQL HNSW index is created after bulk load to reduce indexing overhead.
- Partition `audit_events` and `agent_steps` monthly after growth.
- Move sandbox execution to isolated worker pool to protect API latency.
- For repos over 10k files, index prioritized files first: source, tests, config, docs.

---

# 5. Database Design

## 5.1 Naming Rules

- Table names: plural snake_case.
- Primary keys: `id TEXT PRIMARY KEY` with prefixed ULID strings, e.g. `usr_...`.
- Foreign keys: `<entity>_id TEXT NOT NULL`.
- Timestamps: `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`.
- Soft delete: `deleted_at TIMESTAMPTZ NULL` where required.
- JSON fields: `JSONB NOT NULL DEFAULT '{}'::jsonb`.

## 5.2 Extensions

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
```

## 5.3 Core Schema

```sql
CREATE TYPE workspace_role AS ENUM ('owner', 'admin', 'developer', 'viewer');
CREATE TYPE repository_status AS ENUM ('queued', 'cloning', 'scanning', 'embedding', 'partial_ready', 'ready', 'failed');
CREATE TYPE incident_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE incident_status AS ENUM ('draft', 'queued', 'analyzing', 'analyzed', 'patching', 'testing', 'resolved', 'failed');
CREATE TYPE run_status AS ENUM ('queued', 'running', 'succeeded', 'failed', 'cancelled');
CREATE TYPE patch_status AS ENUM ('draft', 'validating', 'valid', 'invalid', 'accepted', 'rejected');

CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    password_hash TEXT NULL,
    avatar_url TEXT NULL,
    email_verified_at TIMESTAMPTZ NULL,
    last_login_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ NULL
);

CREATE TABLE oauth_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    provider_user_id TEXT NOT NULL,
    provider_email TEXT NOT NULL,
    access_token_encrypted TEXT NULL,
    refresh_token_encrypted TEXT NULL,
    expires_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, provider_user_id)
);

CREATE TABLE refresh_tokens (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    user_agent TEXT NULL,
    ip_address INET NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    created_by_user_id TEXT NOT NULL REFERENCES users(id),
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ NULL
);

CREATE TABLE workspace_members (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role workspace_role NOT NULL DEFAULT 'developer',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workspace_id, user_id)
);

CREATE TABLE repositories (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    remote_url TEXT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    latest_commit_sha TEXT NULL,
    index_status repository_status NOT NULL DEFAULT 'queued',
    index_error TEXT NULL,
    indexed_file_count INTEGER NOT NULL DEFAULT 0,
    indexed_chunk_count INTEGER NOT NULL DEFAULT 0,
    partial_index BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ NULL
);

CREATE TABLE repository_files (
    id TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'unknown',
    content_hash TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    line_count INTEGER NOT NULL,
    is_test BOOLEAN NOT NULL DEFAULT false,
    is_binary BOOLEAN NOT NULL DEFAULT false,
    content TEXT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, path)
);

CREATE TABLE code_symbols (
    id TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_id TEXT NOT NULL REFERENCES repository_files(id) ON DELETE CASCADE,
    symbol_name TEXT NOT NULL,
    symbol_type TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    parent_symbol_id TEXT NULL REFERENCES code_symbols(id) ON DELETE SET NULL,
    signature TEXT NULL,
    docstring TEXT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE code_chunks (
    id TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_id TEXT NOT NULL REFERENCES repository_files(id) ON DELETE CASCADE,
    symbol_id TEXT NULL REFERENCES code_symbols(id) ON DELETE SET NULL,
    chunk_index INTEGER NOT NULL,
    chunk_type TEXT NOT NULL,
    language TEXT NOT NULL,
    path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (file_id, chunk_index)
);

CREATE TABLE chunk_embeddings (
    id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL UNIQUE REFERENCES code_chunks(id) ON DELETE CASCADE,
    repository_id TEXT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    embedding_model TEXT NOT NULL,
    embedding vector(3072) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE incidents (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    repository_id TEXT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    created_by_user_id TEXT NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    severity incident_severity NOT NULL DEFAULT 'medium',
    status incident_status NOT NULL DEFAULT 'draft',
    environment TEXT NOT NULL DEFAULT 'unknown',
    expected_behavior TEXT NULL,
    actual_behavior TEXT NULL,
    stack_trace TEXT NULL,
    logs TEXT NULL,
    reproduction_steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    final_summary TEXT NULL,
    confidence_score NUMERIC(5,2) NULL CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ NULL
);

CREATE TABLE agent_runs (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    run_type TEXT NOT NULL,
    status run_status NOT NULL DEFAULT 'queued',
    model_name TEXT NOT NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    error_code TEXT NULL,
    error_message TEXT NULL,
    input_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    token_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE agent_steps (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    step_name TEXT NOT NULL,
    status run_status NOT NULL DEFAULT 'queued',
    sequence_number INTEGER NOT NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, sequence_number)
);

CREATE TABLE retrieval_results (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    vector_score NUMERIC(10,6) NULL,
    keyword_score NUMERIC(10,6) NULL,
    rerank_score NUMERIC(10,6) NULL,
    reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, chunk_id)
);

CREATE TABLE patch_sets (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    status patch_status NOT NULL DEFAULT 'draft',
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    unified_diff TEXT NOT NULL,
    validation_errors JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_level TEXT NOT NULL DEFAULT 'medium',
    created_by TEXT NOT NULL DEFAULT 'ai',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE patch_files (
    id TEXT PRIMARY KEY,
    patch_set_id TEXT NOT NULL REFERENCES patch_sets(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    change_type TEXT NOT NULL,
    rationale TEXT NOT NULL,
    old_content_hash TEXT NULL,
    new_content_hash TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sandbox_runs (
    id TEXT PRIMARY KEY,
    patch_set_id TEXT NOT NULL REFERENCES patch_sets(id) ON DELETE CASCADE,
    status run_status NOT NULL DEFAULT 'queued',
    command TEXT NOT NULL,
    exit_code INTEGER NULL,
    stdout TEXT NULL,
    stderr TEXT NULL,
    summary TEXT NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    duration_ms INTEGER NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NULL REFERENCES workspaces(id) ON DELETE SET NULL,
    actor_user_id TEXT NULL REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NULL,
    ip_address INET NULL,
    user_agent TEXT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 5.4 Indexes

```sql
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_repositories_workspace ON repositories(workspace_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_repository_files_repo_path ON repository_files(repository_id, path);
CREATE INDEX idx_code_symbols_repo_name ON code_symbols(repository_id, symbol_name);
CREATE INDEX idx_code_chunks_repo_file ON code_chunks(repository_id, file_id);
CREATE INDEX idx_code_chunks_search ON code_chunks USING GIN(search_vector);
CREATE INDEX idx_code_chunks_path_trgm ON code_chunks USING GIN(path gin_trgm_ops);
CREATE INDEX idx_chunk_embeddings_hnsw ON chunk_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_incidents_workspace_status ON incidents(workspace_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_incidents_repo_created ON incidents(repository_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_agent_runs_incident_created ON agent_runs(incident_id, created_at DESC);
CREATE INDEX idx_agent_steps_run_sequence ON agent_steps(run_id, sequence_number);
CREATE INDEX idx_retrieval_results_run_rank ON retrieval_results(run_id, rank);
CREATE INDEX idx_patch_sets_incident ON patch_sets(incident_id, created_at DESC);
CREATE INDEX idx_sandbox_runs_patch ON sandbox_runs(patch_set_id, created_at DESC);
CREATE INDEX idx_audit_workspace_created ON audit_events(workspace_id, created_at DESC);
```

## 5.5 Sample Data Structure

```json
{
  "repository": {
    "id": "repo_01JZABCDEF0000000000000000",
    "name": "demo-fastapi-auth",
    "index_status": "ready",
    "indexed_file_count": 284,
    "indexed_chunk_count": 913
  },
  "incident": {
    "id": "inc_01JZABCDEG0000000000000000",
    "title": "Login returns 500 after expired token",
    "severity": "high",
    "status": "analyzed",
    "confidence_score": 87.5
  },
  "retrieval_result": {
    "path": "app/auth/service.py",
    "start_line": 72,
    "end_line": 102,
    "rerank_score": 0.9421,
    "reason": "Stack trace references this function and it handles expired token user lookup."
  }
}
```

## 5.6 Migration and Seeding Approach

- Use Alembic for all schema changes.
- Migration files must be deterministic and reversible where practical.
- Do not modify already-applied migration files.
- Seed script creates:
  - Demo user: `demo@devsentinel.local`
  - Demo workspace
  - Demo repository metadata
  - Demo incident
- Seed script must never run in production unless `ALLOW_PROD_SEED=true`.

---

# 6. AI Workflow

## 6.1 Workflow Overview

```mermaid
stateDiagram-v2
    [*] --> Triage
    Triage --> QueryPlanning
    QueryPlanning --> HybridRetrieval
    HybridRetrieval --> Rerank
    Rerank --> ContextAssembly
    ContextAssembly --> RootCauseAnalysis
    RootCauseAnalysis --> RiskAssessment
    RiskAssessment --> PatchPlanning
    PatchPlanning --> PatchGeneration
    PatchGeneration --> PatchValidation
    PatchValidation --> FinalReport
    FinalReport --> [*]
```

## 6.2 Agent Nodes

| Node | Model | Input | Output |
|---|---|---|---|
| Triage | gpt-5-mini | Incident fields | Bug category, severity confirmation, query hints |
| QueryPlanning | gpt-5-mini | Triage result | Search queries, file path guesses, symbol guesses |
| HybridRetrieval | no LLM | Query plan | Candidate chunks from vector + FTS |
| Rerank | gpt-5-mini | Candidate chunks | Top ranked chunks and reasons |
| ContextAssembly | no LLM | Top chunks | Token-budgeted context pack |
| RootCauseAnalysis | gpt-5.2 | Context pack | Root cause, evidence, confidence |
| RiskAssessment | gpt-5-mini | Proposed root cause | risk level, blast radius, missing evidence |
| PatchPlanning | gpt-5.2 | root cause + files | per-file change plan |
| PatchGeneration | gpt-5.2 | change plan + file content | unified diff |
| PatchValidation | no LLM + optional gpt-5-mini | diff | validated patch or errors |
| FinalReport | gpt-5-mini | all outputs | concise final incident report |

## 6.3 Retrieval Mechanism

### Hybrid Search Query

1. Extract keywords from incident title, stack trace, exception type, function names, file names, endpoint paths, log keys.
2. Generate 3 to 6 semantic queries.
3. Run vector search against `chunk_embeddings`.
4. Run PostgreSQL full-text search against `code_chunks.search_vector`.
5. Add path-trigram matches for stack-trace file paths.
6. Merge candidates by weighted score.
7. Rerank with LLM using title, error, and candidate snippets.

### Retrieval SQL Pattern

```sql
WITH vector_candidates AS (
    SELECT
        cc.id AS chunk_id,
        1 - (ce.embedding <=> :query_embedding) AS vector_score,
        NULL::float AS keyword_score
    FROM chunk_embeddings ce
    JOIN code_chunks cc ON cc.id = ce.chunk_id
    WHERE ce.repository_id = :repository_id
    ORDER BY ce.embedding <=> :query_embedding
    LIMIT 40
),
keyword_candidates AS (
    SELECT
        cc.id AS chunk_id,
        NULL::float AS vector_score,
        ts_rank_cd(cc.search_vector, plainto_tsquery('english', :query_text)) AS keyword_score
    FROM code_chunks cc
    WHERE cc.repository_id = :repository_id
      AND cc.search_vector @@ plainto_tsquery('english', :query_text)
    ORDER BY keyword_score DESC
    LIMIT 40
)
SELECT chunk_id,
       max(vector_score) AS vector_score,
       max(keyword_score) AS keyword_score
FROM (
    SELECT * FROM vector_candidates
    UNION ALL
    SELECT * FROM keyword_candidates
) merged
GROUP BY chunk_id
LIMIT 60;
```

## 6.4 Context Assembly Strategy

Token budget: 120,000 input tokens maximum for root-cause analysis.

Priority order:

1. Exact file paths referenced in stack trace.
2. Chunks containing exception line/function.
3. Direct callers/callees from symbol graph.
4. Related tests.
5. Relevant config files.
6. README/docs explaining behavior.
7. Prior agent findings.

Context pack format:

```text
<incident>
Title: ...
Severity: ...
Stack trace: ...
Logs: ...
</incident>

<retrieved_chunk id="chk_..." path="app/auth/service.py" lines="72-102" score="0.94">
...
</retrieved_chunk>

<retrieved_chunk id="chk_..." path="tests/test_auth.py" lines="10-88" score="0.88">
...
</retrieved_chunk>
```

## 6.5 Prompt Templates

### 6.5.1 Triage Prompt

```text
You are the triage node in DevSentinel AI.
Classify the incident using only the provided incident fields.
Do not infer facts not present in the input.
Return strict JSON matching the schema.

Incident:
{{ incident_json }}

Schema:
{
  "bug_category": "auth|database|api|frontend|config|dependency|unknown",
  "severity_assessment": "low|medium|high|critical",
  "search_terms": ["string"],
  "path_hints": ["string"],
  "symbol_hints": ["string"],
  "missing_information": ["string"]
}
```

### 6.5.2 Root Cause Prompt

```text
You are the root-cause analysis node in DevSentinel AI.
Use only the incident and retrieved code context.
Every technical claim must cite at least one chunk id.
If evidence is insufficient, say so.
Do not invent files, functions, APIs, tests, or behavior.
Return strict JSON.

Incident and context:
{{ context_pack }}

Required JSON schema:
{
  "root_cause": "string",
  "evidence": [
    {
      "claim": "string",
      "chunk_id": "string",
      "path": "string",
      "lines": "string"
    }
  ],
  "confidence_score": 0,
  "recommended_fix": "string",
  "files_likely_to_change": ["string"],
  "tests_to_run": ["string"],
  "missing_evidence": ["string"]
}
```

### 6.5.3 Patch Generation Prompt

```text
You are the patch generation node in DevSentinel AI.
Generate a unified diff only.
Rules:
- Modify only files listed in the approved change plan.
- Preserve existing style.
- Include tests when feasible.
- Do not touch secrets, generated files, lockfiles, or binary files.
- Output must be valid unified diff, no markdown fences.

Approved change plan:
{{ change_plan_json }}

Relevant file contents:
{{ file_context }}
```

## 6.6 Response Parsing and Validation

- All structured LLM outputs must be parsed into Pydantic models.
- Invalid JSON triggers one repair attempt using `gpt-5-mini`.
- If repair fails, mark agent step `failed` with `AI_OUTPUT_SCHEMA_INVALID`.
- Confidence score must be numeric from 0 to 100.
- Evidence chunk IDs must exist in `retrieval_results` for that run.
- Patch output must pass diff parser before saving as `valid`.

## 6.7 Fallback Mechanisms

| Failure | Fallback |
|---|---|
| Embedding API timeout | Retry 5 times with exponential backoff; then mark repo `partial_ready` if enough chunks indexed |
| No retrieval results | Ask for more incident context; do not generate root cause |
| LLM rate limit | Queue retry with delay and show `waiting_on_provider` step |
| Invalid AI JSON | Run repair prompt once, then fail gracefully |
| Patch invalid | Save as `invalid` with parser errors and allow regenerate |
| Sandbox unavailable | Still show patch and explain validation was not executed |

## 6.8 Quality Assurance Checks

- Root-cause answer must include at least 2 evidence citations unless repository has fewer relevant chunks.
- Patch generation cannot start unless root-cause confidence >= 60.
- Risk level is `high` if patch modifies auth, payments, migrations, or security-sensitive code.
- Generated patch must not include environment variables or secrets.
- Analysis output must include `missing_evidence` when confidence < 75.

---

# 7. Security Implementation

## 7.1 Authentication Flow

- Access tokens are JWTs with 15-minute expiry.
- Refresh tokens are opaque random 256-bit tokens stored only as hashes.
- Refresh token rotation is mandatory.
- Passwords are hashed with Argon2id.
- GitHub OAuth accounts must have verified email.
- Cookies for refresh tokens use `HttpOnly`, `Secure`, `SameSite=Lax`.
- Access token can be stored in memory on frontend; never localStorage.

## 7.2 Authorization Rules

| Endpoint Group | Owner | Admin | Developer | Viewer |
|---|---|---|---|---|
| Workspace settings | yes | yes | no | no |
| Invite/manage members | yes | yes | no | no |
| Import repository | yes | yes | yes | no |
| Delete repository | yes | yes | no | no |
| Create incident | yes | yes | yes | no |
| Analyze incident | yes | yes | yes | no |
| Generate patch | yes | yes | yes | no |
| Run sandbox | yes | yes | yes | no |
| View incidents/repos | yes | yes | yes | yes |
| Audit logs | yes | yes | no | no |

## 7.3 Input Validation and Sanitization

- All API bodies use Pydantic schemas.
- Strip control characters from titles and descriptions.
- Normalize line endings to `\n`.
- Reject HTML in user text unless explicitly rendered as escaped text.
- Repository URLs must use `https://github.com/...` for v1.
- File uploads must be ZIP MIME and checked by magic bytes.
- Extract ZIP with zip-slip protection: reject paths containing `..` or absolute roots.
- Reject files larger than configured limits.

## 7.4 SQL Injection Prevention

- Use SQLAlchemy parameter binding for all queries.
- Never build SQL with string concatenation from user input.
- For dynamic sort fields, use an allowlist mapping.
- Full-text search input must be passed as bound parameter to `plainto_tsquery`.

## 7.5 XSS and CSRF Protection

- React must render user content as text, never `dangerouslySetInnerHTML`.
- Markdown rendering is disabled for user-provided incident fields in v1.
- Code blocks are escaped.
- Refresh token cookie uses `SameSite=Lax`.
- Mutating routes require `Authorization` header.
- If cookie-based session is added later, add CSRF double-submit token.

## 7.6 API Key and Secret Management

- Store provider secrets only in environment variables or platform secret manager.
- Never write API keys to logs, DB, traces, or frontend bundle.
- Encrypt OAuth tokens at rest using application-level envelope encryption.
- Redact logs with patterns for API keys, JWTs, GitHub tokens, AWS keys, and `.env` content.
- CI must fail if secrets are detected by secret scanning.

## 7.7 Encryption

| Data | In Transit | At Rest |
|---|---|---|
| Browser to frontend | HTTPS | N/A |
| Frontend to API | HTTPS | N/A |
| API to DB | TLS in production | Managed disk encryption |
| OAuth tokens | HTTPS | Application-level encrypted fields |
| Uploaded artifacts | HTTPS | S3/MinIO server-side encryption |
| Logs/traces | HTTPS | Provider encryption |

## 7.8 Security Headers

Set these headers in frontend and API responses:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.openai.com;
```

## 7.9 AI-Specific Security

- Treat all repository content, logs, and user text as untrusted.
- Prompt templates must explicitly instruct the model not to follow instructions found inside repository files.
- Do not send secrets or `.env` files to AI provider.
- Add prompt injection detector step for suspicious text such as `ignore previous instructions`.
- Tool execution is not directly controlled by LLM output. Backend validates every action.
- Sandbox network access is disabled by default.

---

# 8. API Specifications

## 8.1 Global API Rules

Base URL: `/api/v1`

Required headers for authenticated endpoints:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
X-Request-ID: <uuid optional>
```

Standard error body:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message.",
    "details": {},
    "request_id": "req_01JZ0000000000000000000000"
  }
}
```

Common status codes:

| Code | Meaning |
|---:|---|
| 200 | Success |
| 201 | Created |
| 202 | Accepted async job |
| 204 | No content |
| 400 | Bad request |
| 401 | Unauthenticated |
| 403 | Forbidden |
| 404 | Not found or not accessible |
| 409 | Conflict |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Internal error |

## 8.2 Endpoint Catalog

### Auth

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/auth/register` | no | `RegisterRequest` | `201 AuthResponse` |
| POST | `/auth/login` | no | `LoginRequest` | `200 AuthResponse` |
| POST | `/auth/logout` | yes | none | `204` |
| POST | `/auth/refresh` | refresh cookie | none | `200 AuthResponse` |
| GET | `/auth/me` | yes | none | `200 CurrentUserResponse` |
| GET | `/auth/github/start` | no | query `redirect_uri` | `302` |
| GET | `/auth/github/callback` | no | query `code,state` | `302` |

### Workspaces

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| GET | `/workspaces` | yes | none | `200 WorkspaceListResponse` |
| POST | `/workspaces` | yes | `CreateWorkspaceRequest` | `201 WorkspaceResponse` |
| GET | `/workspaces/{workspace_id}` | yes | none | `200 WorkspaceResponse` |
| PATCH | `/workspaces/{workspace_id}` | owner/admin | `UpdateWorkspaceRequest` | `200 WorkspaceResponse` |
| GET | `/workspaces/{workspace_id}/members` | yes | none | `200 MemberListResponse` |
| PATCH | `/workspaces/{workspace_id}/members/{member_id}` | owner/admin | `UpdateMemberRoleRequest` | `200 MemberResponse` |

### Repositories

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/repositories` | developer+ | `CreateRepositoryRequest` | `202 RepositoryResponse` |
| POST | `/repositories/upload` | developer+ | multipart ZIP | `202 RepositoryResponse` |
| GET | `/repositories` | viewer+ | query `workspace_id` | `200 RepositoryListResponse` |
| GET | `/repositories/{repository_id}` | viewer+ | none | `200 RepositoryResponse` |
| DELETE | `/repositories/{repository_id}` | admin+ | none | `204` |
| POST | `/repositories/{repository_id}/reindex` | developer+ | none | `202 RepositoryResponse` |
| GET | `/repositories/{repository_id}/files` | viewer+ | query `path_prefix` | `200 FileTreeResponse` |
| GET | `/repositories/{repository_id}/files/{file_id}` | viewer+ | none | `200 FileContentResponse` |

### Incidents

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/incidents` | developer+ | `CreateIncidentRequest` | `201 IncidentResponse` |
| GET | `/incidents` | viewer+ | query filters | `200 IncidentListResponse` |
| GET | `/incidents/{incident_id}` | viewer+ | none | `200 IncidentDetailResponse` |
| PATCH | `/incidents/{incident_id}` | developer+ | `UpdateIncidentRequest` | `200 IncidentResponse` |
| POST | `/incidents/{incident_id}/analyze` | developer+ | `AnalyzeIncidentRequest` | `202 AgentRunResponse` |
| GET | `/incidents/{incident_id}/runs` | viewer+ | none | `200 AgentRunListResponse` |

### Agent Runs

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| GET | `/agent-runs/{run_id}` | viewer+ | none | `200 AgentRunDetailResponse` |
| GET | `/agent-runs/{run_id}/events` | viewer+ | SSE | `text/event-stream` |
| POST | `/agent-runs/{run_id}/cancel` | developer+ | none | `202 AgentRunResponse` |

### Patches and Sandbox

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/incidents/{incident_id}/patches` | developer+ | `GeneratePatchRequest` | `202 PatchSetResponse` |
| GET | `/patches/{patch_id}` | viewer+ | none | `200 PatchSetDetailResponse` |
| POST | `/patches/{patch_id}/validate` | developer+ | none | `200 PatchValidationResponse` |
| POST | `/patches/{patch_id}/revise` | developer+ | `RevisePatchRequest` | `202 PatchSetResponse` |
| POST | `/patches/{patch_id}/export` | viewer+ | none | `200 ExportPatchResponse` |
| POST | `/patches/{patch_id}/sandbox-runs` | developer+ | `CreateSandboxRunRequest` | `202 SandboxRunResponse` |
| GET | `/sandbox-runs/{sandbox_run_id}` | viewer+ | none | `200 SandboxRunDetailResponse` |
| GET | `/sandbox-runs/{sandbox_run_id}/events` | viewer+ | SSE | `text/event-stream` |
| POST | `/sandbox-runs/{sandbox_run_id}/cancel` | developer+ | none | `202 SandboxRunResponse` |

## 8.3 Schema Examples

```json
{
  "CreateRepositoryRequest": {
    "workspace_id": "wsp_01JZ...",
    "provider": "github_public_url",
    "url": "https://github.com/example/repo",
    "default_branch": "main"
  },
  "RepositoryResponse": {
    "id": "repo_01JZ...",
    "workspace_id": "wsp_01JZ...",
    "name": "repo",
    "provider": "github_public_url",
    "remote_url": "https://github.com/example/repo",
    "default_branch": "main",
    "index_status": "queued",
    "indexed_file_count": 0,
    "indexed_chunk_count": 0,
    "created_at": "2026-05-11T16:00:00Z"
  }
}
```

## 8.4 SSE Event Format

```text
event: agent_step_started
data: {"run_id":"run_...","step_name":"HybridRetrieval","sequence_number":3}

event: agent_step_completed
data: {"run_id":"run_...","step_name":"HybridRetrieval","summary":"Retrieved 42 candidate chunks"}

event: run_completed
data: {"run_id":"run_...","status":"succeeded"}
```

---

# 9. Testing Strategy

## 9.1 Coverage Targets

| Layer | Target |
|---|---:|
| Backend unit tests | >= 90% for services and domain logic |
| Backend API tests | >= 85% endpoint coverage |
| Frontend component tests | >= 80% critical UI components |
| E2E tests | 100% critical paths |
| AI workflow tests | deterministic fixture coverage for every node |

## 9.2 Backend Unit Tests

Test these modules:

- Auth service: password hashing, JWT issue/verify, refresh rotation.
- RBAC service: role permissions per endpoint.
- Repository scanner: include/exclude rules, language detection.
- Chunker: Python, TypeScript, Markdown fallback behavior.
- Retrieval service: vector/keyword merge and rerank input generation.
- Patch validator: valid/invalid unified diff cases.
- Sandbox command detector.
- Rate limiter.

## 9.3 Integration Tests

| Scenario | Expected Result |
|---|---|
| Register user | User, workspace, owner membership created |
| Import demo repo | Repository queued and task created |
| Index fixture repo | Files, chunks, embeddings persisted |
| Create incident | Incident linked to repo/workspace |
| Run analysis with mocked LLM | Agent steps and retrieval results saved |
| Generate patch with mocked LLM | Patch saved and validated |
| Sandbox run with fake command | Logs and exit code saved |
| Unauthorized workspace access | 404 or 403 according to endpoint policy |

## 9.4 E2E Critical Paths

- Register -> import repo -> see indexing progress.
- Create incident -> run analysis -> see timeline and root-cause panel.
- Generate patch -> view diff -> run sandbox -> see test result.
- Viewer role can view but cannot mutate.
- Expired token refresh flow works without losing current page.

## 9.5 Performance Benchmarks

| Benchmark | Target |
|---|---:|
| API health endpoint | P95 < 50 ms |
| Repository list | P95 < 250 ms |
| File tree for 10k files | P95 < 800 ms cached |
| Incident detail | P95 < 300 ms |
| SSE event latency | P95 < 500 ms |
| Index 1k-file repo | < 3 minutes |
| Hybrid retrieval | P95 < 1.5 seconds |

## 9.6 Security Testing Checklist

- [ ] Password brute force returns 429.
- [ ] User cannot access another workspace's repository.
- [ ] ZIP slip archive is rejected.
- [ ] `.env` and secret-like files are not indexed.
- [ ] Prompt injection inside repo file does not alter system instructions.
- [ ] XSS payload in incident title renders escaped.
- [ ] SQL injection strings do not affect queries.
- [ ] Refresh token reuse revokes all sessions.
- [ ] Sandbox cannot access network after dependency phase.
- [ ] API keys are redacted from logs.

## 9.7 Test Data Management

- Use fixture repositories under `backend/tests/fixtures/repos`.
- Use fake embedding provider returning deterministic vectors.
- Use mocked LLM provider for CI.
- Use ephemeral PostgreSQL test DB per test session.
- Use transaction rollback for API tests where possible.
- Never call real OpenAI API in default CI.

---

# 10. Deployment Pipeline

## 10.1 Environments

| Environment | Purpose | Data |
|---|---|---|
| local | Developer iteration | Local Docker volumes |
| test | CI automated tests | Ephemeral |
| staging | Pre-prod validation | Sanitized/demo data |
| production | Public portfolio demo | Real user data |

## 10.2 Required Environment Variables

```bash
APP_ENV=local
APP_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql+psycopg://devsentinel:devsentinel@postgres:5432/devsentinel
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change-me-32-byte-minimum
JWT_ISSUER=devsentinel-ai
JWT_AUDIENCE=devsentinel-web
REFRESH_COOKIE_NAME=ds_refresh
OPENAI_API_KEY=sk-...
OPENAI_REASONING_MODEL=gpt-5.2
OPENAI_FAST_MODEL=gpt-5-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OBJECT_STORAGE_ENDPOINT=http://minio:9000
OBJECT_STORAGE_BUCKET=devsentinel-artifacts
OBJECT_STORAGE_ACCESS_KEY=minioadmin
OBJECT_STORAGE_SECRET_KEY=minioadmin
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
ALLOW_PROD_SEED=false
```

## 10.3 Local Docker Compose Services

```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    env_file: .env.local
    depends_on: [api]

  api:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env.local
    depends_on: [postgres, redis, minio]

  worker-ai:
    build: ./backend
    command: celery -A app.worker.celery_app worker -Q ai,indexing -l INFO
    env_file: .env.local
    depends_on: [postgres, redis]

  worker-sandbox:
    build: ./backend
    command: celery -A app.worker.celery_app worker -Q sandbox -l INFO
    env_file: .env.local
    depends_on: [postgres, redis]

  postgres:
    image: pgvector/pgvector:0.8.2-pg18
    environment:
      POSTGRES_USER: devsentinel
      POSTGRES_PASSWORD: devsentinel
      POSTGRES_DB: devsentinel
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:8.0-alpine
    ports: ["6379:6379"]

  minio:
    image: minio/minio:RELEASE.2026-04-22T22-12-26Z
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    volumes: ["miniodata:/data"]

volumes:
  pgdata:
  miniodata:
```

## 10.4 Build Process

Frontend:

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Backend:

```bash
uv sync --frozen
ruff check .
ruff format --check .
mypy app
pytest --cov=app --cov-report=term-missing
alembic upgrade head
```

## 10.5 Migration Strategy

- Run migrations automatically during deployment release phase, not during app startup.
- Always back up production DB before destructive migrations.
- Use expand-and-contract for breaking schema changes.
- Add nullable columns first, backfill, then enforce NOT NULL in later migration.

## 10.6 Rollback Procedure

1. Stop new deployments.
2. Roll back application image to previous version.
3. If migration is reversible and caused issue, run `alembic downgrade -1` only after data impact review.
4. If irreversible, apply forward fix migration.
5. Re-run smoke tests.
6. Create incident note in `audit_events`.

## 10.7 Monitoring and Alerting

Alerts:

- API 5xx rate > 2% for 5 minutes.
- P95 API latency > 1 second for 10 minutes.
- Celery queue depth > 100 for 10 minutes.
- Worker task failure rate > 10% for 10 minutes.
- Database connections > 80% max.
- OpenAI error rate > 20% for 10 minutes.
- Sandbox timeout rate > 30%.

Dashboards:

- API latency by route.
- Error rate by service.
- Worker queue depth.
- AI token usage and cost by workspace.
- Repository indexing duration.
- Incident analysis duration.
- Sandbox run pass/fail counts.

---

# 11. Code Standards and Conventions

## 11.1 Repository Structure

```text
devsentinel-ai/
  frontend/
    app/
      (auth)/
      app/
      api/
    components/
      ui/
      layout/
      repositories/
      incidents/
      patches/
      shared/
    lib/
      api/
      auth/
      stores/
      schemas/
      utils/
    tests/
  backend/
    app/
      api/
        routes/
        dependencies.py
      core/
        config.py
        security.py
        logging.py
      db/
        models/
        migrations/
        session.py
      services/
        auth_service.py
        repository_service.py
        indexing_service.py
        retrieval_service.py
        incident_service.py
        patch_service.py
        sandbox_service.py
      ai/
        graphs/
        prompts/
        schemas.py
        providers.py
      worker/
        celery_app.py
        tasks.py
      tests/
    alembic.ini
  infra/
    docker/
    github-actions/
  docs/
    info.md
```

## 11.2 Backend Coding Rules

- Use async FastAPI route handlers where I/O is involved.
- Keep route handlers thin; business logic belongs in services.
- All service methods must use explicit typed inputs and outputs.
- Use SQLAlchemy 2.0 style queries.
- Use Pydantic schemas for request and response models.
- Raise domain-specific exceptions and map them to API errors centrally.
- Every log entry must include `request_id` when available.
- Never log secrets, tokens, raw authorization headers, or full stack traces containing secrets.

### Backend Error Pattern

```python
class AppError(Exception):
    code: str = "APP_ERROR"
    status_code: int = 400

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)
```

## 11.3 Frontend Coding Rules

- Use server components by default.
- Use client components only for interactivity.
- All API calls go through `lib/api/client.ts`.
- All forms use `react-hook-form` and `zod` schemas.
- Components must be small and named by domain.
- UI state belongs in Zustand only when shared across sibling routes/components.
- Server state belongs in TanStack Query.
- Avoid prop drilling beyond two levels.
- Use `loading.tsx`, `error.tsx`, and skeleton components for route segments.

### Component Pattern

```tsx
export function IncidentSummaryCard({ incident }: IncidentSummaryCardProps) {
  return (
    <Card className="rounded-2xl border border-zinc-800 bg-zinc-950/80 shadow-xl">
      <CardHeader>
        <CardTitle className="text-base font-semibold tracking-tight">
          {incident.title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Render escaped text only. */}
      </CardContent>
    </Card>
  )
}
```

## 11.4 Logging Standards

Structured JSON logs fields:

```json
{
  "timestamp": "2026-05-11T16:00:00Z",
  "level": "INFO",
  "service": "api",
  "request_id": "req_...",
  "user_id": "usr_...",
  "workspace_id": "wsp_...",
  "event": "incident.analysis.started",
  "metadata": {}
}
```

## 11.5 Comment Requirements

- Do not comment obvious code.
- Comment security-sensitive decisions.
- Comment AI prompt assumptions.
- Comment non-trivial SQL queries.
- Public functions/classes require docstrings in backend service layer.

## 11.6 Formatting

Backend:

- Ruff format line length: 100.
- Mypy strict mode for `app/services`, `app/ai`, `app/core`.
- Imports sorted by Ruff.

Frontend:

- Prettier default formatting.
- ESLint with Next.js recommended rules.
- TypeScript strict mode.
- No `any` unless justified with inline comment.

---

# 12. Limitations and Constraints

## 12.1 Known Technical Debt

- v1 uses public GitHub URL import instead of full GitHub App installation.
- Sandbox test execution may need provider-specific hardening before enterprise use.
- LLM-based reranking adds cost and latency.
- Single PostgreSQL database handles both app data and vectors; may need split later.
- No multi-tenant per-workspace encryption keys in v1.

## 12.2 Performance Bottlenecks

| Bottleneck | Mitigation |
|---|---|
| Embedding large repositories | Batch embeddings, partial indexing, caching by content hash |
| HNSW index build time | Build after bulk insert, tune maintenance_work_mem |
| Large file trees | Cache tree response, virtualize frontend list |
| Long AI context | Summarize lower-priority docs, strict token budget |
| Sandbox cold starts | Keep warm worker pool in production |

## 12.3 Third-Party API Limitations

- OpenAI rate limits vary by account tier.
- Model behavior may change for alias models; snapshot models should be used when reproducibility matters.
- GitHub anonymous clone rate limits can affect public repo imports.
- Vercel serverless functions are not ideal for long-running indexing; use backend worker service.

## 12.4 Browser and Device Compatibility

- Support latest Chrome, Firefox, Safari, and Edge.
- Mobile support is responsive but optimized for review, not heavy code editing.
- Monaco editor loads only on desktop/tablet widths >= 768px; mobile shows read-only code blocks.
- Minimum supported viewport width: 360px.

## 12.5 Scalability Limits for v1

| Limit | Value |
|---|---:|
| Max repository size | 50 MB ZIP or 10k indexed files |
| Max file indexed | 512 KB |
| Max incident logs | 200 KB stored inline |
| Max AI analyses per workspace/day | 20 |
| Max patch generations per incident/day | 5 |
| Max sandbox runtime | 180 seconds |
| Max concurrent sandbox runs per workspace | 1 |

---

# 13. Future Roadmap

## 13.1 Priority 1 - Strong Resume Enhancements

- [ ] GitHub pull request creation from accepted patch.
- [ ] Interactive architecture graph of repository dependencies.
- [ ] AI-generated test case suggestions with one-click patch inclusion.
- [ ] Cost dashboard showing tokens, model, and estimated spend.
- [ ] Public shareable incident report with redacted code snippets.

## 13.2 Priority 2 - Production Hardening

- [ ] GitHub App installation for private repos.
- [ ] SSO/SAML for teams.
- [ ] Per-workspace API usage budgets.
- [ ] Workspace-level encryption keys.
- [ ] Advanced sandbox isolation using Firecracker/microVMs.

## 13.3 Priority 3 - AI Quality Improvements

- [ ] Offline eval suite with labeled incidents.
- [ ] Automatic regression tests for prompts.
- [ ] Cross-encoder reranker service.
- [ ] Repository-level architectural summaries.
- [ ] Multi-model comparison mode.

## 13.4 Priority 4 - Integrations

- [ ] Jira issue import/export.
- [ ] Linear issue import/export.
- [ ] Slack incident summary notifications.
- [ ] Sentry issue import.
- [ ] Datadog log import.

---

# 14. Implementation Checklist

## 14.1 Foundation

- [ ] Initialize monorepo with `frontend`, `backend`, `infra`, and `docs`.
- [ ] Create Docker Compose local environment.
- [ ] Configure PostgreSQL 18 + pgvector.
- [ ] Configure Redis.
- [ ] Configure MinIO.
- [ ] Add backend FastAPI app skeleton.
- [ ] Add frontend Next.js app skeleton.
- [ ] Add CI workflow.

## 14.2 Backend

- [ ] Implement config management.
- [ ] Implement structured logging.
- [ ] Implement DB session and base models.
- [ ] Implement Alembic migrations.
- [ ] Implement auth service.
- [ ] Implement RBAC dependencies.
- [ ] Implement repository import service.
- [ ] Implement indexing service.
- [ ] Implement retrieval service.
- [ ] Implement AI workflow graph.
- [ ] Implement incident service.
- [ ] Implement patch service.
- [ ] Implement sandbox service.
- [ ] Implement audit logging.

## 14.3 Frontend

- [ ] Implement design tokens and global styles.
- [ ] Implement auth pages.
- [ ] Implement app shell/sidebar/topbar.
- [ ] Implement repository list and import dialog.
- [ ] Implement repository detail and file explorer.
- [ ] Implement incident create/list/detail pages.
- [ ] Implement agent timeline with SSE.
- [ ] Implement root-cause and citations UI.
- [ ] Implement patch diff viewer.
- [ ] Implement sandbox logs view.
- [ ] Implement settings page.

## 14.4 AI

- [ ] Define Pydantic AI output schemas.
- [ ] Add prompt templates.
- [ ] Add fake provider for tests.
- [ ] Add OpenAI provider.
- [ ] Add embedding batcher.
- [ ] Add hybrid retrieval.
- [ ] Add reranking.
- [ ] Add context assembly.
- [ ] Add patch validation.

## 14.5 Security and Quality

- [ ] Add rate limiting.
- [ ] Add security headers.
- [ ] Add ZIP upload hardening.
- [ ] Add secret redaction.
- [ ] Add dependency scanning.
- [ ] Add test coverage gates.
- [ ] Add OpenTelemetry instrumentation.
- [ ] Add Sentry integration.
- [ ] Add deployment docs.

---

# Final AI Assistant Notes

When generating code from this document:

1. Start with the monorepo structure.
2. Implement database models and migrations before APIs.
3. Implement auth and RBAC before protected resources.
4. Implement repository import and indexing before AI analysis.
5. Implement AI provider abstraction before real OpenAI calls.
6. Implement frontend pages against typed API contracts.
7. Add tests at the same time as features.
8. Do not skip security, error handling, or loading states.
9. Keep code production-ready and interview-explainable.
10. Preserve the naming, endpoints, schema, UI, and workflow defined here.
