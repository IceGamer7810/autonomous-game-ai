"""Strict parsing of a model response into an action proposal."""

import json
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from game_agent.contracts import ActionProposal


class ActionParseError(ValueError):
    """Raised when a model response is not a valid structured action."""


def parse_action(response: str | Mapping[str, Any]) -> ActionProposal:
    """Parse only structured JSON/object responses; never execute raw text."""

    try:
        payload: Any = json.loads(response) if isinstance(response, str) else response
    except json.JSONDecodeError as error:
        raise ActionParseError("model response is not valid JSON") from error
    if not isinstance(payload, Mapping):
        raise ActionParseError("model response must be an object")
    try:
        return ActionProposal.model_validate(payload)
    except ValidationError as error:
        raise ActionParseError("model response failed action validation") from error
