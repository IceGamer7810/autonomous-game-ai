from game_agent.health import check_health


def test_health_check_does_not_require_external_services():
    result = check_health()
    assert result.status == "ok"
    assert result.checks["runtime"] == "ok"
