"""Cautious experiment tracking without game-specific assumptions."""

from dataclasses import dataclass
from enum import StrEnum


class ExplorerState(StrEnum):
    IDLE = "idle"
    PROBING = "probing"
    EVALUATING = "evaluating"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Experiment:
    id: str
    precondition: str
    action_description: str
    expected_effect: str
    max_attempts: int = 1


class Explorer:
    def __init__(self) -> None:
        self.state = ExplorerState.IDLE
        self._attempts: dict[str, int] = {}

    def begin(self, experiment: Experiment) -> None:
        attempts = self._attempts.get(experiment.id, 0)
        if attempts >= experiment.max_attempts:
            self.state = ExplorerState.BLOCKED
            raise ValueError("experiment attempt limit reached")
        self._attempts[experiment.id] = attempts + 1
        self.state = ExplorerState.PROBING

    def evaluate(self, experiment_id: str, observed_effect: str, succeeded: bool) -> None:
        if self.state is not ExplorerState.PROBING:
            raise ValueError("no experiment is currently probing")
        self.state = ExplorerState.EVALUATING
        if not succeeded:
            self.state = ExplorerState.BLOCKED
        else:
            self.state = ExplorerState.IDLE
