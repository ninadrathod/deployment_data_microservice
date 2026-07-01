# models.py - DATA CONTRACT ONLY (no FastAPI imports here)

from pydantic import BaseModel, Field # BaseModel = schema class; Field = field rules
from typing import Literal # Literal = allowed enum values for status field

# Alias for readability - same as writing Literal[...] inline on every model
Status = Literal["success", "failed", "rolled_back"]

class Deployment(BaseModel):
    id: str
    service: str
    status: Status
    duration: int = Field(ge=0, description="Duration in seconds")
    timestamp: str # keep as str; ISO format validated by convention
    commit_sha: str

class MetricData(BaseModel):
    service: str
    failure_rate: float
    deployment_rate: float
    p95_duration: float | None