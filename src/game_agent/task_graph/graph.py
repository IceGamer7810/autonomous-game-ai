"""Small DAG implementation with explicit state transitions."""

from dataclasses import dataclass, field
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"


@dataclass
class TaskNode:
    id: str
    description: str
    priority: int = 0
    dependencies: set[str] = field(default_factory=set)
    completion_evidence: str = ""
    status: TaskStatus = TaskStatus.PENDING


class TaskGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, TaskNode] = {}

    def add(self, node: TaskNode) -> None:
        if node.id in self._nodes:
            raise ValueError(f"duplicate task: {node.id}")
        if node.id in node.dependencies:
            raise ValueError("task cannot depend on itself")
        unknown = node.dependencies - self._nodes.keys()
        if unknown:
            raise ValueError(f"unknown dependencies: {sorted(unknown)}")
        self._nodes[node.id] = node

    def ready(self) -> list[TaskNode]:
        ready = [
            node
            for node in self._nodes.values()
            if node.status is TaskStatus.PENDING
            and all(self._nodes[dependency].status is TaskStatus.COMPLETED for dependency in node.dependencies)
        ]
        return sorted(ready, key=lambda node: node.priority, reverse=True)

    def start(self, task_id: str) -> None:
        node = self._nodes[task_id]
        if node not in self.ready():
            raise ValueError("task is not ready")
        node.status = TaskStatus.RUNNING

    def finish(self, task_id: str, success: bool) -> None:
        node = self._nodes[task_id]
        if node.status is not TaskStatus.RUNNING:
            raise ValueError("only running tasks can finish")
        node.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

    def get(self, task_id: str) -> TaskNode:
        return self._nodes[task_id]
