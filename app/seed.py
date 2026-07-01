# contains the seed data for the deployment store
# To be used in the main.py file for API routes

import random
from datetime import datetime, timedelta, timezone

random.seed(30)
# produces the same “random” choices (same services, statuses, durations, etc.).

SERVICES = ["billing-api","auth-service","notifications","frontend-web"]
STATUSES = ["success","failed","rolled_back"]

def generate_deployements(count: int = 35) -> list[dict]:
    """ Generate a list of deployments """
    now = datetime.now(timezone.utc)
    out = []
    for i in range(count):
        # Random deployment time within the past 28 days.
        ts = now - timedelta(hours=random.randint(0, 28 * 24))
        out.append({
            "id": f"deploy_{i:03d}", # produces deploy_001, deploy_002, etc.
            "service": random.choice(SERVICES),
            "status": random.choice(STATUSES),
            "duration": random.randint(60, 900), # 1-15 minutes
            "timestamp": ts.isoformat().replace("+00:00", "Z"), # ISO format with Z for UTC
            "commit_sha": random.randbytes(3).hex()
        })
    return out