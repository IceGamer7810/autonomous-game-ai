"""Single-writer safety boundary for operating-system input."""

from .arbiter import ArbitrationResult, InputArbiter

__all__ = ["ArbitrationResult", "InputArbiter"]
