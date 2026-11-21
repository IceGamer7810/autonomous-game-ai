from game_agent.session import SessionManager, SessionState


def test_session_rejects_stale_generation_and_releases_on_pause_stop():
    releases = []
    manager = SessionManager(lambda: releases.append(True))
    first = manager.start("window", "goal")
    manager.pause()
    assert manager.state is SessionState.PAUSED
    manager.resume()
    second = manager.start("window", "new goal")
    assert first.session_id != second.session_id
    assert not manager.accepts(first.session_id)
    assert manager.accepts(second.session_id)
    manager.stop()
    assert manager.state is SessionState.STOPPED
    assert len(releases) >= 3
