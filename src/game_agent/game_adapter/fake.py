"""Deterministic fake adapters used by safety and replay tests."""

from dataclasses import dataclass, field

from game_agent.contracts import ActionProposal
from game_agent.game_adapter.frame_buffer import Frame, FrameBuffer


@dataclass
class FakeInput:
    dispatched: list[ActionProposal] = field(default_factory=list)
    release_count: int = 0

    def dispatch(self, action: ActionProposal) -> None:
        self.dispatched.append(action)

    def release_all(self) -> None:
        self.release_count += 1


class FakeCapture:
    def __init__(self, capacity: int = 4) -> None:
        self.frames: FrameBuffer[bytes] = FrameBuffer(capacity)

    def capture(self, payload: bytes, timestamp: float) -> Frame[bytes]:
        return self.frames.append(payload, timestamp)
