# main.py - HTTP LAYER ONLY
# Routes stay thin; logic lives in store/ and services/

from typing import List, Optional, Literal
# List = return type of multiple deployments
# Optional = query filters may be omitted (None = no filter)

from fastapi import FastAPI, HTTPException, Query
# FastAPI = framework; creates app and routes
# HTTPException = raise 404, 400 with JSON {"detail": "..."}
# Query = declare ?service= or ?status= parameters in URL

from .models import Deployment, MetricData
from .seed import generate_deployements
from .store import DeploymentStore
from services.metrics import DEFAULT_TIME_RANGE, MetricOps

# =============================================================================
# FastAPI app setup
# "app" is what uvicorn runs
# =============================================================================
app = FastAPI(
    title="Deployment Tracker",
    version="1.0.0",
)

store = DeploymentStore()
metric_ops = MetricOps()
Deployement_Status = Literal["success", "failed", "rolled_back"]
Deployment_Service = Literal["billing-api","auth-service","notifications","frontend-web"]

""" Load seed data on startup """
@app.on_event("startup")
def on_startup() -> None:
    raw = generate_deployements()
    deployments = [Deployment(**item) for item in raw]
    store.load(deployments)

""" List all deployments, optionally filtered by service or status """
@app.get("/deployments", response_model=List[Deployment])
def list_deployments(
    service: Optional[Deployment_Service] = Query(None, description="Filter by service"),
    status: Optional[Deployement_Status] = Query(None, description="Filter by status"),
) -> List[Deployment]:
    return store.list(service=service, status=status)

""" Get a deployment by ID """
@app.get("/deployments/{deployment_id}", response_model=Deployment)
def get_deployment(deployment_id: str) -> Deployment:
    deployment = store.get(deployment_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

""" Per-service deployment metrics over a rolling time window """
@app.get("/metrics", response_model=List[MetricData])
def get_metrics(
    time_range: int = Query(
        DEFAULT_TIME_RANGE,
        ge=1,
        description="Rolling window in days",
    ),
) -> List[MetricData]:
    try:
        return metric_ops.calculate_metrics(store, time_range=time_range)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

""" Health check """
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}