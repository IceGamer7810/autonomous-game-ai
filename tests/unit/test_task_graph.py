import pytest

from game_agent.task_graph import TaskGraph, TaskNode, TaskStatus


def test_task_graph_enforces_dependencies_and_completion():
    graph = TaskGraph()
    graph.add(TaskNode("first", "first"))
    graph.add(TaskNode("second", "second", dependencies={"first"}))
    assert [task.id for task in graph.ready()] == ["first"]
    graph.start("first")
    graph.finish("first", success=True)
    assert [task.id for task in graph.ready()] == ["second"]
    assert graph.get("first").status is TaskStatus.COMPLETED


def test_task_graph_rejects_unknown_dependency():
    graph = TaskGraph()
    with pytest.raises(ValueError, match="unknown"):
        graph.add(TaskNode("task", "task", dependencies={"missing"}))
