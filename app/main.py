# main.py - HTTP LAYER ONLY
# Routes stay thin; logic lives in store/ and services/

from typing import List, Optional
# List = return type of multiple deployments
# Optional = query filters may be omitted (None = no filter)

from fastapi import FastAPI, HTTPException, Query
# FastAPI = framework; creates app and routes
# HTTPException = raise 404, 400 with JSON {"detail": "..."}
# Query = declare ?service= or ?status= parameters in URL

from .models import Deployment
from .seed import generate_deployements
from .store import DeploymentStore

# =============================================================================
# FastAPI app setup
# "app" is what uvicorn runs
# =============================================================================
app = FastAPI(
    title="Deployment Tracker",
    version="1.0.0",
)

store = DeploymentStore()

""" Load seed data on startup """
@app.on_event("startup")
def on_startup() -> None:
    raw = generate_deployements()
    deployments = [Deployment(**item) for item in raw]
    store.load(deployments)

""" List all deployments, optionally filtered by service or status """
@app.get("/deployments", response_model=List[Deployment])
def list_deployments(
    service: Optional[str] = Query(None, description="Filter by service"),
    status: Optional[str] = Query(None, description="Filter by status"),
) -> List[Deployment]:
    return store.list(service=service, status=status)

""" Get a deployment by ID """
@app.get("/deployments/{deployment_id}", response_model=Deployment)
def get_deployment(deployment_id: str) -> Deployment:
    deployment = store.get(deployment_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

""" Health check """
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}