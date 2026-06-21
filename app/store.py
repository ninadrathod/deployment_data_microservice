# contains all the functions for DeploymentStore class
# To be used in the main.py file for API routes

from typing import Dict, List, Optional
# Dict = Dictionary of deployments: {deployment_id: Deployment}
# List = ordered collection of Deployment objects
# Optional = parameter may be str OR None (filter not applied when None)

from .models import Deployment # relative import - same package (app/)

class DeploymentStore:

    def __init__(self):
        # In-memory database: {"deploy_001": Deployment(...), ...}
        self._data: Dict[str, Deployment] = {}

    def load(self, deployments: List[Deployment]):
        """ Load deployments into in-memory database """
        self._data = {d.id: d for d in deployments}

    def list(
        self,
        service: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Deployment]:
        """ List deployments, optionally filtered by service or status """
        results = list(self._data.values()) # copy to avoid modifying original
        if service is not None:
            results = [d for d in results if d.service == service]
        if status is not None:
            results = [d for d in results if d.status == status]
        # Newest first
        results.sort(key=lambda d: d.timestamp, reverse=True)
        return results

    def get(self, deployment_id: str) -> Optional[Deployment]:
        """ Returns Deployment or None - route layer converts None -> HTTP 404 """
        return self._data.get(deployment_id)