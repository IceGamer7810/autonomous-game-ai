"""Configurable OpenAI-compatible Player-1 client."""

import base64
import json
import os
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from game_agent.config import Player1Config

from .parser import ActionParseError, parse_action


class Transport(Protocol):
    async def post(self, url: str, *, headers: Mapping[str, str], json: Any, timeout: float) -> Any: ...


@dataclass(frozen=True)
class RequestTiming:
    total_seconds: float
    attempts: int


@dataclass(frozen=True)
class Player1Result:
    action: Any
    timing: RequestTiming


class Player1Client:
    """Request tactical actions without exposing transport or OS privileges."""

    def __init__(
        self,
        config: Player1Config,
        *,
        transport: Transport,
        environ: Mapping[str, str] | None = None,
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._config = config
        self._transport = transport
        self._environ = environ if environ is not None else os.environ
        self._sleep = sleep

    async def request_action(
        self,
        *,
        image: bytes,
        instruction: str,
        session_id: str,
        window_id: str,
        issued_at_monotonic: float,
        expires_at_monotonic: float,
    ) -> Player1Result:
        """Send one bounded request and parse one strict action proposal."""

        encoded_image = base64.b64encode(image).decode("ascii")
        payload = {
            "model": self._config.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}},
                    ],
                }
            ],
        }
        api_key = self._environ.get(self._config.api_key_env)
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        started = time.monotonic()
        last_error: Exception | None = None
        for attempt in range(1, self._config.max_retries + 2):
            try:
                response = await self._transport.post(
                    f"{self._config.endpoint.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self._config.timeout_seconds,
                )
                response_payload = _response_json(response)
                arguments = _extract_tool_arguments(response_payload)
                action_payload = _with_request_context(
                    arguments,
                    session_id=session_id,
                    window_id=window_id,
                    issued_at_monotonic=issued_at_monotonic,
                    expires_at_monotonic=expires_at_monotonic,
                )
                action = parse_action(action_payload)
                return Player1Result(action=action, timing=RequestTiming(time.monotonic() - started, attempt))
            except (ActionParseError, OSError, TimeoutError, ValueError, httpx.HTTPError) as error:
                last_error = error
                if attempt <= self._config.max_retries and self._sleep is not None:
                    await self._sleep(0)
        raise RuntimeError("Player-1 request failed after bounded retries") from last_error


def _response_json(response: Any) -> Mapping[str, Any]:
    if isinstance(response, Mapping):
        return response
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    if hasattr(response, "json"):
        value = response.json()
        if isinstance(value, Mapping):
            return value
    raise ValueError("transport response did not contain a JSON object")


def _extract_tool_arguments(response: Mapping[str, Any]) -> str | Mapping[str, Any]:
    try:
        tool_calls = response["choices"][0]["message"]["tool_calls"]
        arguments = tool_calls[0]["function"]["arguments"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("response did not contain a Player-1 tool call") from error
    if not isinstance(arguments, (str, Mapping)):
        raise ValueError("tool-call arguments must be JSON text or an object")
    return arguments


def _with_request_context(
    arguments: str | Mapping[str, Any],
    *,
    session_id: str,
    window_id: str,
    issued_at_monotonic: float,
    expires_at_monotonic: float,
) -> Mapping[str, Any]:
    if isinstance(arguments, str):
        try:
            decoded = json.loads(arguments)
        except json.JSONDecodeError as error:
            raise ValueError("tool-call arguments are not valid JSON") from error
    else:
        decoded = dict(arguments)
    if not isinstance(decoded, Mapping):
        raise ValueError("tool-call arguments must decode to an object")
    payload = dict(decoded)
    payload.update(
        session_id=session_id,
        window_id=window_id,
        issued_at_monotonic=issued_at_monotonic,
        expires_at_monotonic=expires_at_monotonic,
    )
    return payload
