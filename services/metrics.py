# Reusable metrics logic — no FastAPI imports

from datetime import datetime, timedelta, timezone
from math import ceil

from app.models import Deployment, MetricData
from app.store import DeploymentStore

DEFAULT_TIME_RANGE = 7


def _current_time_iso() -> str:
    """Return current UTC time in ISO-8601 format with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _cutoff_date(time_range: int) -> str:
    """Return ISO timestamp for time_range days before the current UTC time."""
    now = _parse_timestamp(_current_time_iso())
    cutoff = now - timedelta(days=time_range)
    return cutoff.isoformat().replace("+00:00", "Z")


def _parse_timestamp(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _is_within_time_range(timestamp: str, cutoff_date: str) -> bool:
    """True when deployment timestamp is on or after cutoff_date."""
    return _parse_timestamp(timestamp) >= _parse_timestamp(cutoff_date)


def _p95(values: list[int]) -> float | None:
    if len(values) < 5:
        return None
    sorted_values = sorted(values)
    index = min(ceil(0.95 * len(sorted_values)) - 1, len(sorted_values) - 1)
    return float(sorted_values[index])


class MetricOps:

    def calculate_metrics(
        self,
        store: DeploymentStore,
        time_range: int = DEFAULT_TIME_RANGE,
    ) -> list[MetricData]:
        if time_range <= 0:
            raise ValueError("time_range must be greater than 0")

        deployments = store.list()
        cutoff = _cutoff_date(time_range)
        in_range = [
            d for d in deployments
            if _is_within_time_range(d.timestamp, cutoff)
        ]

        by_service: dict[str, list[Deployment]] = {}
        for deployment in in_range:
            by_service.setdefault(deployment.service, []).append(deployment)

        metrics: list[MetricData] = []
        for service, group in sorted(by_service.items()):
            total = len(group)
            failures = sum(1 for d in group if d.status == "failed")
            metrics.append(
                MetricData(
                    service=service,
                    failure_rate=failures / total if total else 0.0,
                    deployment_rate=total / time_range,
                    p95_duration=_p95([d.duration for d in group]),
                )
            )
        return metrics
