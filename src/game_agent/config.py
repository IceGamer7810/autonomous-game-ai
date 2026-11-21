"""Configuration loading with explicit, bounded defaults."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Player1Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    endpoint: str = "http://127.0.0.1:8000/v1"
    model: str = "yyyang/Player-1-9B"
    api_key_env: str = "PLAYER1_API_KEY"
    timeout_seconds: float = Field(default=30, gt=0, le=300)
    max_retries: int = Field(default=1, ge=0, le=3)


class CaptureConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_fps: int = Field(default=30, ge=1, le=60)
    frame_buffer_capacity: int = Field(default=8, ge=1, le=256)


class ApiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = "127.0.0.1"
    port: int = Field(default=8765, ge=1, le=65535)


class LoggingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str = "INFO"


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player1: Player1Config = Player1Config()
    capture: CaptureConfig = CaptureConfig()
    api: ApiConfig = ApiConfig()
    logging: LoggingConfig = LoggingConfig()


class EnvironmentSettings(BaseSettings):
    """Environment overrides for deployment secrets and endpoint settings."""

    model_config = SettingsConfigDict(
        env_prefix="GAME_AGENT_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    player1_endpoint: str | None = None
    player1_model: str | None = None
    player1_api_key_env: str | None = None
    player1_timeout_seconds: float | None = None
    player1_max_retries: int | None = None
    capture_target_fps: int | None = None
    frame_buffer_capacity: int | None = None
    api_host: str | None = None
    api_port: int | None = None
    log_level: str | None = None


def load_config(path: Path | None = None) -> AgentConfig:
    """Load YAML configuration and apply supported environment overrides."""

    raw: dict[str, Any] = {}
    if path is not None:
        with path.open(encoding="utf-8") as config_file:
            loaded = yaml.safe_load(config_file) or {}
            if not isinstance(loaded, dict):
                raise ValueError("configuration root must be a mapping")
            raw = loaded

    config = AgentConfig.model_validate(raw)
    environment = EnvironmentSettings()
    updates: dict[str, Any] = {}

    player1_updates = {
        "endpoint": environment.player1_endpoint,
        "model": environment.player1_model,
        "api_key_env": environment.player1_api_key_env,
        "timeout_seconds": environment.player1_timeout_seconds,
        "max_retries": environment.player1_max_retries,
    }
    if any(value is not None for value in player1_updates.values()):
        updates["player1"] = config.player1.model_copy(
            update={key: value for key, value in player1_updates.items() if value is not None}
        )
    capture_updates = {
        "target_fps": environment.capture_target_fps,
        "frame_buffer_capacity": environment.frame_buffer_capacity,
    }
    if any(value is not None for value in capture_updates.values()):
        updates["capture"] = config.capture.model_copy(
            update={key: value for key, value in capture_updates.items() if value is not None}
        )
    api_updates = {"host": environment.api_host, "port": environment.api_port}
    if any(value is not None for value in api_updates.values()):
        updates["api"] = config.api.model_copy(
            update={key: value for key, value in api_updates.items() if value is not None}
        )
    if environment.log_level is not None:
        updates["logging"] = config.logging.model_copy(update={"level": environment.log_level})
    return config.model_copy(update=updates)
