import pytest

from game_agent.config import Player1Config
from game_agent.player1_client.client import Player1Client


class FakeTransport:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    async def post(self, url, *, headers, json, timeout):
        self.calls += 1
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def response(arguments):
    return {"choices": [{"message": {"tool_calls": [{"function": {"arguments": arguments}}]}}]}


@pytest.mark.asyncio
async def test_client_extracts_action_and_measures_request():
    transport = FakeTransport(
        [
            response(
                '{"action_type":"wait","priority":60,'
                '"issued_at_monotonic":0,"expires_at_monotonic":1}'
            )
        ]
    )
    client = Player1Client(
        Player1Config(max_retries=0),
        transport=transport,
        environ={},
    )
    result = await client.request_action(
        image=b"png",
        instruction="wait",
        session_id="s",
        window_id="w",
        issued_at_monotonic=1,
        expires_at_monotonic=2,
    )
    assert result.action.session_id == "s"
    assert result.timing.total_seconds >= 0
    assert transport.calls == 1


@pytest.mark.asyncio
async def test_client_retries_once_without_exposing_raw_response():
    transport = FakeTransport(
        [
            ValueError("temporary"),
            response(
                '{"action_type":"wait","priority":60,'
                '"issued_at_monotonic":0,"expires_at_monotonic":1}'
            ),
        ]
    )
    client = Player1Client(Player1Config(max_retries=1), transport=transport, environ={})
    result = await client.request_action(
        image=b"png",
        instruction="wait",
        session_id="s",
        window_id="w",
        issued_at_monotonic=1,
        expires_at_monotonic=2,
    )
    assert result.action.window_id == "w"
    assert transport.calls == 2


def test_platform_adapter_rejects_non_windows():
    from game_agent.game_adapter.platform import require_windows

    with pytest.raises(RuntimeError, match="Windows"):
        require_windows()
