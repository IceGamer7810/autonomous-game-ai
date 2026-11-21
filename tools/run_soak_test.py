"""Run a bounded synthetic reliability soak without a game or model endpoint."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from game_agent.game_adapter import FrameBuffer
from game_agent.telemetry import Telemetry


def run(duration_seconds: float) -> dict[str, object]:
    if duration_seconds <= 0:
        raise ValueError("duration must be positive")
    buffer = FrameBuffer[bytes](capacity=8)
    telemetry = Telemetry()
    started = time.monotonic()
    iterations = 0
    while time.monotonic() - started < duration_seconds:
        iterations += 1
        buffer.append(str(iterations).encode(), time.monotonic())
        telemetry.update_capture(30, buffer.dropped_frames, 0)
        telemetry.record_inference(0.001)
        time.sleep(0.001)
    snapshot = telemetry.snapshot()
    return {
        "duration_seconds": time.monotonic() - started,
        "iterations": iterations,
        "buffer_capacity": buffer.capacity,
        "buffer_occupancy": buffer.occupancy,
        "dropped_frames": buffer.dropped_frames,
        "inference_p50_seconds": snapshot.inference_p50_seconds,
        "inference_p95_seconds": snapshot.inference_p95_seconds,
        "fault_injection": {
            "capture_stall": "not_run",
            "focus_loss": "not_run",
            "worker_failure": "not_run",
        },
        "evidence_class": "synthetic bounded harness; not a game soak result",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-seconds", type=float, default=60)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(run(args.duration_seconds), indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
