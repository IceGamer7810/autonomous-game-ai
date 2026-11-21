"""Reflex decisions derived from observable telemetry only."""

from dataclasses import dataclass
from enum import StrEnum


class ReflexReason(StrEnum):
    FOCUS_LOST = "focus_lost"
    CAPTURE_STALLED = "capture_stalled"
    ACTION_TIMEOUT = "action_timeout"
    NO_VISIBLE_PROGRESS = "no_visible_progress"
    REPEATED_ACTION = "repeated_action"


@dataclass(frozen=True)
class ReflexDecision:
    should_stop_input: bool
    reason: ReflexReason


class ReflexWatchdog:
    def evaluate(
        self,
        *,
        focused: bool,
        capture_age_seconds: float,
        max_capture_age_seconds: float,
        action_age_seconds: float,
        action_timeout_seconds: float,
        repeated_frames: int,
        repeated_actions: int,
        threshold: int = 5,
    ) -> ReflexDecision | None:
        if not focused:
            return ReflexDecision(True, ReflexReason.FOCUS_LOST)
        if capture_age_seconds > max_capture_age_seconds:
            return ReflexDecision(True, ReflexReason.CAPTURE_STALLED)
        if action_age_seconds > action_timeout_seconds:
            return ReflexDecision(True, ReflexReason.ACTION_TIMEOUT)
        if repeated_frames >= threshold:
            return ReflexDecision(True, ReflexReason.NO_VISIBLE_PROGRESS)
        if repeated_actions >= threshold:
            return ReflexDecision(True, ReflexReason.REPEATED_ACTION)
        return None
