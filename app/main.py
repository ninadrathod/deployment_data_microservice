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