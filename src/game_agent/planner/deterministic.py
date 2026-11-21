"""Minimal rule-based planner that does not require an LLM."""

from dataclasses import dataclass

from game_agent.task_graph import TaskGraph, TaskNode


@dataclass(frozen=True)
class Plan:
    goal: str
    graph: TaskGraph


class DeterministicPlanner:
    def create_plan(self, goal: str) -> Plan:
        if not goal.strip():
            raise ValueError("goal must not be empty")
        graph = TaskGraph()
        graph.add(
            TaskNode(
                id="observe-and-discover",
                description="Observe the selected window and discover visible controls",
                priority=100,
                completion_evidence="visible control or menu evidence recorded",
            )
        )
        graph.add(
            TaskNode(
                id="pursue-user-goal",
                description=goal.strip(),
                priority=90,
                dependencies={"observe-and-discover"},
                completion_evidence="user-defined visual completion evidence",
            )
        )
        return Plan(goal=goal.strip(), graph=graph)
