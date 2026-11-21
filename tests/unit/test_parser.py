import pytest

from game_agent.player1_client import ActionParseError, parse_action


def test_parser_accepts_only_valid_structured_action():
    action = parse_action(
        '{"session_id":"s","window_id":"w","action_type":"wait",'
        '"priority":60,"issued_at_monotonic":1,"expires_at_monotonic":2}'
    )
    assert action.action_type == "wait"


@pytest.mark.parametrize("response", ["press enter", "[]", '{"action_type":"key_down"}'])
def test_parser_rejects_untrusted_or_incomplete_response(response):
    with pytest.raises(ActionParseError):
        parse_action(response)
