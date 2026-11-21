"""Bounded latest-frame storage."""

from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Frame(Generic[T]):
    payload: T
    captured_at_monotonic: float
    sequence: int


class FrameBuffer(Generic[T]):
    """Thread-safe fixed-capacity buffer that drops the oldest frame."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._frames: deque[Frame[T]] = deque(maxlen=capacity)
        self._capacity = capacity
        self._next_sequence = 0
        self._dropped_frames = 0
        self._lock = Lock()

    def append(self, payload: T, captured_at_monotonic: float) -> Frame[T]:
        with self._lock:
            if len(self._frames) == self._capacity:
                self._dropped_frames += 1
            frame = Frame(payload, captured_at_monotonic, self._next_sequence)
            self._next_sequence += 1
            self._frames.append(frame)
            return frame

    def latest(self) -> Frame[T] | None:
        with self._lock:
            return self._frames[-1] if self._frames else None

    def snapshot(self) -> tuple[Frame[T], ...]:
        with self._lock:
            return tuple(self._frames)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def dropped_frames(self) -> int:
        with self._lock:
            return self._dropped_frames

    @property
    def occupancy(self) -> int:
        with self._lock:
            return len(self._frames)
