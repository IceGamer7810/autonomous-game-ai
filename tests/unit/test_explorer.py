import pytest

from game_agent.explorer import Explorer, ExplorerState, Experiment


def test_explorer_bounds_repeated_experiments():
    explorer = Explorer()
    experiment = Experiment("probe", "visible menu", "press key", "menu changes", max_attempts=1)
    explorer.begin(experiment)
    explorer.evaluate(experiment.id, "no change", succeeded=False)
    assert explorer.state is ExplorerState.BLOCKED
    with pytest.raises(ValueError, match="limit"):
        explorer.begin(experiment)
