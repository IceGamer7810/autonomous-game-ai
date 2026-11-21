"""Hash-based frame change and repeated-frame detection."""

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class FrameChange:
    frame_hash: str
    changed: bool
    repeated_count: int


def compare_frames(previous: bytes | None, current: bytes, repeated_count: int = 0) -> FrameChange:
    current_hash = hashlib.sha256(current).hexdigest()
    previous_hash = hashlib.sha256(previous).hexdigest() if previous is not None else None
    changed = previous_hash != current_hash
    return FrameChange(
        frame_hash=current_hash,
        changed=changed,
        repeated_count=0 if changed else repeated_count + 1,
    )
