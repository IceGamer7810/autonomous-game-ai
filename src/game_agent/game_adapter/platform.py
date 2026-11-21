"""Platform adapter boundaries with explicit unsupported-platform behavior."""

import sys
from typing import Protocol


class CaptureAdapter(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...


class InputAdapter(Protocol):
    def dispatch(self, action) -> None: ...

    def release_all(self) -> None: ...


def require_windows() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Windows capture/input adapters require Windows 10 or 11")
