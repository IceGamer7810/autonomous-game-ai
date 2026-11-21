"""Small bounded metrics collector for dashboard and reports."""

from collections import deque
from dataclasses import dataclass
from statistics import median


@dataclass(frozen=True)
class TelemetrySnapshot:
    capture_fps: float | None
    inference_p50_seconds: float | None
    inference_p95_seconds: float | None
    dropped_frames: int
    queue_occupancy: int


class Telemetry:
    def __init__(self, sample_capacity: int = 1024) -> None:
        if sample_capacity < 1:
            raise ValueError("sample_capacity must be positive")
        self._latencies: deque[float] = deque(maxlen=sample_capacity)
        self._capture_fps: float | None = None
        self._dropped_frames = 0
        self._queue_occupancy = 0

    def record_inference(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("latency cannot be negative")
        self._latencies.append(seconds)

    def update_capture(self, fps: float, dropped_frames: int, queue_occupancy: int) -> None:
        if fps < 0 or dropped_frames < 0 or queue_occupancy < 0:
            raise ValueError("telemetry values cannot be negative")
        self._capture_fps = fps
        self._dropped_frames = dropped_frames
        self._queue_occupancy = queue_occupancy

    def snapshot(self) -> TelemetrySnapshot:
        values = sorted(self._latencies)
        p95 = values[max(0, int(len(values) * 0.95) - 1)] if values else None
        return TelemetrySnapshot(
            capture_fps=self._capture_fps,
            inference_p50_seconds=median(values) if values else None,
            inference_p95_seconds=p95,
            dropped_frames=self._dropped_frames,
            queue_occupancy=self._queue_occupancy,
        )
