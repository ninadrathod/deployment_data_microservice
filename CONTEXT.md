# Project Context

Quick orientation for agents and contributors working on **deployment_data_microservice**.

## What this project is

A small **FastAPI** microservice that tracks software deployment records **in memory**. It is prework for a Zapier AI pair-programming exercise.

On startup, the app loads **35 deterministic seed deployments** (fixed random seed) and exposes REST endpoints to list, filter, and fetch them. There is no database or persistence — data resets when the process restarts.

## How to run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://localhost:8000`
- Interactive docs: `/docs` (Swagger), `/redoc`

Requires **Python 3.10+**.

## Architecture

The codebase follows a strict layered split:

```
HTTP layer          app/main.py       Routes, query/path validation, HTTPException
Data contract       app/models.py     Pydantic Deployment schema (no FastAPI)
Business logic      app/store.py      In-memory DeploymentStore
Seed data           app/seed.py       generate_deployements() — 35 sample records
Shared services     services/         Reusable logic (e.g. metrics); no HTTP imports
```

**Important convention:** All HTTP status codes and error payloads are raised in **`app/main.py` only**. Lower layers return values (`None`, empty lists) or raise domain errors — never `HTTPException`.

See `.cursor/rules/project-workflow.mdc` for the full agent workflow (sync README/requirements, edge-case review, error-handling rules).

## API surface

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check → `{"status": "ok"}` |
| `GET` | `/deployments` | List deployments, newest first |
| `GET` | `/deployments/{deployment_id}` | Single deployment by ID |
| `GET` | `/metrics` | Per-service metrics over a rolling time window |

### Query filters (`GET /deployments`)

| Param | Allowed values |
|-------|----------------|
| `service` | `billing-api`, `auth-service`, `notifications`, `frontend-web` |
| `status` | `success`, `failed`, `rolled_back` |

Both are optional. Omitting them returns all deployments.

### Query filters (`GET /metrics`)

| Param | Notes |
|-------|-------|
| `time_range` | Optional integer, default `7`; rolling window in days, must be ≥ 1 |

### Error behavior

| Case | Status | Body |
|------|--------|------|
| Unknown deployment ID | `404` | `{"detail": "Deployment not found"}` |
| Invalid query enum value | `422` | FastAPI/Pydantic validation detail |
| Invalid `time_range` (≤ 0) | `422` | FastAPI validation detail (`ge=1`) |
| Success | `200` | Deployment JSON, list, or metrics list |

## Data model

`Deployment` (defined in `app/models.py`):

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | e.g. `deploy_001` … `deploy_034` |
| `service` | string | One of four service names |
| `status` | enum | `success`, `failed`, `rolled_back` |
| `duration` | int | Seconds, ≥ 0 |
| `timestamp` | string | ISO-8601 UTC with `Z` suffix |
| `commit_sha` | string | Short hex commit identifier |

`MetricData` (defined in `app/models.py`):

| Field | Type | Notes |
|-------|------|-------|
| `service` | string | Service name |
| `failure_rate` | float | Fraction of failed deployments |
| `deployment_rate` | float | Deployments per time unit |
| `p95_duration` | float or null | 95th percentile duration in seconds; null when fewer than 5 deployments in the window |

## Key implementation details

- **`DeploymentStore`** holds a `Dict[str, Deployment]` keyed by `id`.
- **`store.list()`** filters by optional `service`/`status`, sorts by `timestamp` descending.
- **`store.get()`** returns `Optional[Deployment]`; `main.py` maps `None` → `404`.
- **`MetricOps`** (`services/metrics.py`) computes per-service `MetricData` from `DeploymentStore.list()`, filtered to a rolling UTC window (default 7 days) via ISO timestamp comparison. Raises `ValueError` when `time_range <= 0`.
- **Seed data** uses `random.seed(30)` so service, status, and duration choices are reproducible across restarts; timestamps are spread randomly over the **past 28 days** from startup time.
- Typo in codebase: function is named `generate_deployements` (missing second **n**).

## Root files agents should keep in sync

When changing `app/` or `services/`:

| File | Update when |
|------|-------------|
| `README.md` | Routes, params, examples, setup, or file overview change |
| `requirements.txt` | New Python dependencies are imported |
| `.gitignore` | New generated artifacts or secrets paths appear |
| `CONTEXT.md` | Architecture, API contract, or conventions change |

## Dependencies

- `fastapi` — web framework
- `uvicorn[standard]` — ASGI server
- `pydantic` — request/response validation

## Out of scope (currently)

- No auth, no write endpoints (create/update/delete)
- No external database or caching
- No tests directory yet
