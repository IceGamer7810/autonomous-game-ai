from pathlib import Path

from game_agent.config import load_config


def test_default_config_is_bounded():
    config = load_config()
    assert config.capture.target_fps == 30
    assert config.capture.frame_buffer_capacity > 0
    assert config.api.host == "127.0.0.1"


def test_yaml_config_is_loaded(tmp_path: Path):
    path = tmp_path / "config.yaml"
    path.write_text(
        "capture:\n  target_fps: 15\n  frame_buffer_capacity: 4\n",
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.capture.target_fps == 15
    assert config.capture.frame_buffer_capacity == 4
