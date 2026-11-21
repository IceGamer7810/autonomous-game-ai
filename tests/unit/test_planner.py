from game_agent.planner import DeterministicPlanner


def test_deterministic_planner_creates_dependency_plan():
    plan = DeterministicPlanner().create_plan("reach the visible objective")
    assert plan.goal == "reach the visible objective"
    assert [task.id for task in plan.graph.ready()] == ["observe-and-discover"]
    assert plan.graph.get("pursue-user-goal").dependencies == {"observe-and-discover"}
