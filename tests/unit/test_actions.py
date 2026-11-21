import pytest
from pydantic import ValidationError

from game_agent.contracts import ActionProposal, ActionType, InputPriority


def proposal(**overrides):
    values = {
        "session_id": "session-1",
        "window_id": "window-1",
        "action_type": ActionType.KEY_DOWN,
        "priority": InputPriority.PLAYER1,
        "issued_at_monotonic": 10,
        "expires_at_monotonic": 11,
        "key": "w",
    }
    values.update(overrides)
    return ActionProposal(**values)


def test_valid_keyboard_action():
    assert proposal().key == "w"


@pytest.mark.parametrize(
    "overrides",
    [
        {"key": None},
        {"action_type": ActionType.MOUSE_MOVE, "key": "w"},
        {"action_type": ActionType.MOUSE_DOWN},
        {"action_type": ActionType.WAIT, "key": "w"},
        {"expires_at_monotonic": 9},
    ],
)
def test_invalid_action_is_rejected(overrides):
    with pytest.raises(ValidationError):
        proposal(**overrides)


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        proposal(untrusted_command="do something")
