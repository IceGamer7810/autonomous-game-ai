"""Dependency-free health checks for the local agent process."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HealthStatus:
    """Serializable health result."""

    status: str
    checks: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "checks": self.checks}


def check_health() -> HealthStatus:
    """Report foundation health without contacting a model or game."""

    return HealthStatus(status="ok", checks={"runtime": "ok", "model_endpoint": "not_configured"})
