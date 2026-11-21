"""Explicit session lifecycle with generation-based cancellation."""

from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4


class SessionState(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass(frozen=True)
class SessionContext:
    session_id: str
    window_id: str
    goal: str


class SessionManager:
    def __init__(self, release_all) -> None:
        self._release_all = release_all
        self._state = SessionState.IDLE
        self._context: SessionContext | None = None

    def start(self, window_id: str, goal: str) -> SessionContext:
        if not window_id or not goal.strip():
            raise ValueError("window_id and goal are required")
        self.stop()
        self._context = SessionContext(str(uuid4()), window_id, goal.strip())
        self._state = SessionState.RUNNING
        return self._context

    def pause(self) -> None:
        if self._state is not SessionState.RUNNING:
            raise ValueError("session is not running")
        self._state = SessionState.PAUSED
        self._release_all()

    def resume(self) -> None:
        if self._state is not SessionState.PAUSED:
            raise ValueError("session is not paused")
        self._state = SessionState.RUNNING

    def stop(self) -> None:
        self._release_all()
        self._state = SessionState.STOPPED if self._context else SessionState.IDLE

    def accepts(self, session_id: str) -> bool:
        return self._state in (SessionState.RUNNING, SessionState.PAUSED) and bool(
            self._context and self._context.session_id == session_id
        )

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def context(self) -> SessionContext | None:
        return self._context
