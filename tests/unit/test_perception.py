from game_agent.perception import compare_frames


def test_perception_detects_repeated_and_changed_frames():
    first = compare_frames(None, b"one")
    repeated = compare_frames(b"one", b"one", first.repeated_count)
    changed = compare_frames(b"one", b"two", repeated.repeated_count)
    assert first.changed
    assert repeated.repeated_count == 1
    assert changed.changed
    assert changed.repeated_count == 0
