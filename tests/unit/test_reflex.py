from game_agent.reflex import ReflexReason, ReflexWatchdog


def test_reflex_stops_for_focus_loss_before_other_conditions():
    decision = ReflexWatchdog().evaluate(
        focused=False,
        capture_age_seconds=99,
        max_capture_age_seconds=1,
        action_age_seconds=99,
        action_timeout_seconds=1,
        repeated_frames=99,
        repeated_actions=99,
    )
    assert decision.reason is ReflexReason.FOCUS_LOST


def test_reflex_is_idle_when_telemetry_is_healthy():
    assert (
        ReflexWatchdog().evaluate(
            focused=True,
            capture_age_seconds=0.1,
            max_capture_age_seconds=1,
            action_age_seconds=0.1,
            action_timeout_seconds=1,
            repeated_frames=0,
            repeated_actions=0,
        )
        is None
    )
