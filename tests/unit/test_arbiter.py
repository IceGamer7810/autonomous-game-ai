from game_agent.contracts import ActionProposal, ActionType, InputPriority
from game_agent.game_adapter.fake import FakeInput
from game_agent.input_arbiter import InputArbiter


def action(**updates):
    values = {
        "session_id": "s",
        "window_id": "w",
        "action_type": ActionType.KEY_DOWN,
        "priority": InputPriority.PLAYER1,
        "issued_at_monotonic": 1,
        "expires_at_monotonic": 3,
        "key": "w",
    }
    values.update(updates)
    return ActionProposal(**values)


def test_arbiter_dispatches_valid_action_and_releases_on_focus_loss():
    executor = FakeInput()
    arbiter = InputArbiter(executor, session_id="s", window_id="w")
    assert arbiter.submit(action(), now_monotonic=2).accepted
    assert arbiter.held_keys == frozenset({"w"})

    arbiter.set_focus(False)
    assert arbiter.held_keys == frozenset()
    assert executor.release_count == 1


def test_arbiter_rejects_stale_window_and_expired_action():
    executor = FakeInput()
    arbiter = InputArbiter(executor, session_id="s", window_id="w")
    assert arbiter.submit(action(window_id="other"), now_monotonic=2).reason == "window_mismatch"
    assert arbiter.submit(action(expires_at_monotonic=1), now_monotonic=2).reason == "expired"
    assert not executor.dispatched


def test_emergency_stop_blocks_pending_actions_and_releases():
    executor = FakeInput()
    arbiter = InputArbiter(executor, session_id="s", window_id="w")
    arbiter.submit(action(), now_monotonic=2)
    arbiter.emergency_stop()
    result = arbiter.submit(action(action_type=ActionType.KEY_UP), now_monotonic=2)
    assert result.reason == "emergency_stop"
    assert executor.release_count == 1
