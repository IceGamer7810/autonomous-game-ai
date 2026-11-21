"""Strict, model-independent input action contracts."""

from enum import IntEnum, StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ActionType(StrEnum):
    """Supported keyboard and mouse operations."""

    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    WAIT = "wait"


class MouseButton(StrEnum):
    """Buttons accepted by the initial input adapter."""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class InputPriority(IntEnum):
    """Input arbitration order, highest priority first."""

    EMERGENCY_STOP = 100
    SAFETY = 90
    REFLEX = 80
    USER = 70
    PLAYER1 = 60
    EXPLORER = 50


class ActionProposal(BaseModel):
    """Validated proposal submitted to the Input Arbiter.

    This contract carries no executable behavior. Platform adapters remain the
    only layer allowed to translate an accepted proposal into OS input.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    session_id: str = Field(min_length=1)
    window_id: str = Field(min_length=1)
    action_type: ActionType
    priority: InputPriority
    issued_at_monotonic: float = Field(ge=0)
    expires_at_monotonic: float = Field(ge=0)
    duration_ms: int = Field(default=200, ge=0, le=10_000)
    key: str | None = Field(default=None, min_length=1, max_length=32)
    button: MouseButton | None = None
    x: int | None = Field(default=None, ge=0)
    y: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_action_fields(self) -> "ActionProposal":
        if self.expires_at_monotonic < self.issued_at_monotonic:
            raise ValueError("expires_at_monotonic must not precede issued_at_monotonic")
        if self.action_type in (ActionType.KEY_DOWN, ActionType.KEY_UP):
            if self.key is None:
                raise ValueError("keyboard actions require key")
            if self.button is not None or self.x is not None or self.y is not None:
                raise ValueError("keyboard actions cannot include mouse fields")
        elif self.action_type in (ActionType.MOUSE_DOWN, ActionType.MOUSE_UP):
            if self.button is None:
                raise ValueError("mouse button actions require button")
            if self.key is not None:
                raise ValueError("mouse button actions cannot include key")
        elif self.action_type is ActionType.MOUSE_MOVE:
            if self.x is None or self.y is None:
                raise ValueError("mouse movement requires x and y")
            if self.key is not None or self.button is not None:
                raise ValueError("mouse movement cannot include key or button")
        elif self.action_type is ActionType.WAIT:
            if any(value is not None for value in (self.key, self.button, self.x, self.y)):
                raise ValueError("wait actions cannot include input fields")
        return self
