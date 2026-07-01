# deployment_data_microservice

Prework for _Zapier AI Pair Programming round_

A small FastAPI microservice that tracks deployment records in memory. It exposes REST endpoints to list, filter, and fetch deployments, with seed data generated on startup.

---

## Setup

Run these commands on any machine with **Python 3.10+** installed.

```bash
# Clone the repository
git clone <your-repo-url>
cd deployment_data_microservice

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (PowerShell)

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

To stop the server, press `Ctrl+C` in the terminal.

---

## Accessing the APIs

### Interactive docs (Swagger UI)

Open in a browser:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/deployments` | List all deployments (optional filters) |
| `GET` | `/deployments/{deployment_id}` | Get a single deployment by ID |
| `GET` | `/metrics` | Per-service metrics over a rolling time window |

### Query parameters (`GET /deployments`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `service` | string (optional) | Filter by service name (e.g. `billing-api`) |
| `status` | string (optional) | Filter by status: `success`, `failed`, or `rolled_back` |

### Query parameters (`GET /metrics`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `time_range` | integer (optional, default `7`) | Rolling window in days; must be ≥ 1 |

### Example requests

```bash
# Health check
curl http://localhost:8000/health

# List all deployments
curl http://localhost:8000/deployments

# Filter by service
curl "http://localhost:8000/deployments?service=billing-api"

# Filter by status
curl "http://localhost:8000/deployments?status=success"

# Filter by both service and status
curl "http://localhost:8000/deployments?service=auth-service&status=failed"

# Get a single deployment by ID
curl http://localhost:8000/deployments/deploy_001

# Per-service metrics (default 7-day window)
curl http://localhost:8000/metrics

# Metrics over a 14-day window
curl "http://localhost:8000/metrics?time_range=14"
```

### Example responses

**`GET /health`**

```json
{"status": "ok"}
```

**`GET /deployments/deploy_001`**

```json
{
  "id": "deploy_001",
  "service": "billing-api",
  "status": "success",
  "duration": 420,
  "timestamp": "2026-06-22T14:30:00Z",
  "commit_sha": "a1b2c3"
}
```

**`GET /deployments/unknown-id`** returns `404` with:

```json
{"detail": "Deployment not found"}
```

**`GET /metrics`**

```json
[
  {
    "service": "auth-service",
    "failure_rate": 0.42857142857142855,
    "deployment_rate": 1.0,
    "p95_duration": 601.0
  },
  {
    "service": "billing-api",
    "failure_rate": 0.1111111111111111,
    "deployment_rate": 1.2857142857142858,
    "p95_duration": 626.0
  }
]
```

**`GET /metrics?time_range=0`** returns `422` with a FastAPI validation error (`time_range` must be ≥ 1).

---

## Cursor project rules

This repo includes an always-applied Cursor rule at `.cursor/rules/project-workflow.mdc`. It tells the AI (and documents for humans) how to work in this codebase:

1. **Sync root docs** — When `app/` or `services/` code changes, update `README.md`, `requirements.txt`, and `.gitignore` in the same task.
2. **Edge cases and HTTP codes** — Consider invalid inputs; use `404` for not found, `400`/`422` for bad input, `200` on success.
3. **Errors in `main.py` only** — Routes raise `HTTPException`; `store.py`, `models.py`, and `services/` return values or domain errors, never HTTP responses.

---

## Project files

| File | Description |
|------|-------------|
| `README.md` | Project documentation (setup, API usage, file overview). |
| `CONTEXT.md` | Agent onboarding: architecture, API contract, conventions, and what to keep in sync. |
| `requirements.txt` | Python dependencies: FastAPI, Uvicorn, and Pydantic. |
| `.cursor/rules/project-workflow.mdc` | Always-applied Cursor rule: sync root docs after app changes, evaluate edge cases, keep HTTP errors in `main.py`. |
| `app/main.py` | FastAPI application entry point. Defines HTTP routes (`/health`, `/deployments`, `/metrics`), loads seed data on startup, and delegates business logic to the store and services. |
| `app/models.py` | Pydantic data models. Defines `Deployment` (with allowed `status` values) and `MetricData` (service metrics). |
| `app/store.py` | In-memory data store (`DeploymentStore`). Handles loading, listing (with optional filters), and fetching deployments by ID. |
| `app/seed.py` | Generates sample deployment data (35 records across 4 services) with timestamps in the past 28 days; loaded on startup. |
| `services/metrics.py` | `MetricOps` — filters deployments by time range and computes per-service `MetricData` (failure rate, deployment rate, p95 duration). |
