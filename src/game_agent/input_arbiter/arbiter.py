"""Input authorization independent of any platform-specific executor."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from game_agent.contracts import ActionProposal, ActionType, InputPriority, MouseButton


class RejectReason(StrEnum):
    EMERGENCY_STOP = "emergency_stop"
    SESSION_MISMATCH = "session_mismatch"
    WINDOW_MISMATCH = "window_mismatch"
    UNFOCUSED = "unfocused"
    EXPIRED = "expired"
    LOWER_PRIORITY = "lower_priority"
    CONCURRENT_OWNER = "concurrent_owner"
    INVALID_KEY = "invalid_key"
    OUT_OF_BOUNDS = "out_of_bounds"


@dataclass(frozen=True)
class ArbitrationResult:
    accepted: bool
    reason: str


class InputExecutor(Protocol):
    def dispatch(self, action: ActionProposal) -> None: ...

    def release_all(self) -> None: ...


class InputArbiter:
    """Authorizes actions and is the only caller of the executor."""

    DEFAULT_KEYS = frozenset(
        set("abcdefghijklmnopqrstuvwxyz0123456789")
        | {
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
            "enter",
            "escape",
            "space",
            "tab",
            "shift",
            "ctrl",
            "alt",
            "up",
            "down",
            "left",
            "right",
        }
    )

    def __init__(
        self,
        executor: InputExecutor,
        *,
        session_id: str,
        window_id: str,
        screen_size: tuple[int, int] = (1920, 1080),
        allowed_keys: frozenset[str] | None = None,
    ) -> None:
        self._executor = executor
        self._session_id = session_id
        self._window_id = window_id
        self._screen_width, self._screen_height = screen_size
        self._allowed_keys = allowed_keys or self.DEFAULT_KEYS
        self._emergency_stop = False
        self._focused = True
        self._owner: InputPriority | None = None
        self._held_keys: set[str] = set()
        self._held_buttons: set[MouseButton] = set()

    def submit(self, action: ActionProposal, *, now_monotonic: float) -> ArbitrationResult:
        if self._emergency_stop:
            return self._reject(RejectReason.EMERGENCY_STOP)
        if action.session_id != self._session_id:
            return self._reject(RejectReason.SESSION_MISMATCH)
        if action.window_id != self._window_id:
            return self._reject(RejectReason.WINDOW_MISMATCH)
        if not self._focused:
            return self._reject(RejectReason.UNFOCUSED)
        if now_monotonic > action.expires_at_monotonic:
            return self._reject(RejectReason.EXPIRED)
        if self._owner is not None and action.priority < self._owner:
            return self._reject(RejectReason.LOWER_PRIORITY)
        if action.action_type in (ActionType.KEY_DOWN, ActionType.KEY_UP):
            if action.key not in self._allowed_keys:
                return self._reject(RejectReason.INVALID_KEY)
        if action.x is not None and action.x >= self._screen_width:
            return self._reject(RejectReason.OUT_OF_BOUNDS)
        if action.y is not None and action.y >= self._screen_height:
            return self._reject(RejectReason.OUT_OF_BOUNDS)
        self._owner = action.priority
        self._executor.dispatch(action)
        if action.action_type is ActionType.KEY_DOWN:
            self._held_keys.add(action.key)  # type narrowing follows validation
        elif action.action_type is ActionType.KEY_UP:
            self._held_keys.discard(action.key)
        elif action.action_type is ActionType.MOUSE_DOWN:
            self._held_buttons.add(action.button)
        elif action.action_type is ActionType.MOUSE_UP:
            self._held_buttons.discard(action.button)
        if not self._held_keys and not self._held_buttons:
            self._owner = None
        return ArbitrationResult(True, "accepted")

    def set_focus(self, focused: bool) -> None:
        self._focused = focused
        if not focused:
            self.release_all()

    def emergency_stop(self) -> None:
        self._emergency_stop = True
        self.release_all()

    def clear_emergency_stop(self) -> None:
        self._emergency_stop = False

    def release_all(self) -> None:
        self._executor.release_all()
        self._held_keys.clear()
        self._held_buttons.clear()
        self._owner = None

    @property
    def held_keys(self) -> frozenset[str]:
        return frozenset(self._held_keys)

    @property
    def held_buttons(self) -> frozenset[MouseButton]:
        return frozenset(self._held_buttons)

    @staticmethod
    def _reject(reason: RejectReason) -> ArbitrationResult:
        return ArbitrationResult(False, reason.value)
