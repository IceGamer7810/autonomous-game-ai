"""Windows DXcam and SendInput adapters.

Imports are delayed so the foundation and fake backend remain usable on other
platforms. These adapters route only through the explicitly supplied window
identity and never inspect titles or game files.
"""

import ctypes
import sys
from ctypes import wintypes
from typing import Any

from game_agent.contracts import ActionProposal, ActionType, MouseButton

from .platform import require_windows


class WindowsCaptureAdapter:
    def __init__(self, window_id: int) -> None:
        require_windows()
        try:
            import dxcam
        except ImportError as error:
            raise RuntimeError("DXcam is required for Windows capture") from error
        self._camera = dxcam.create(output_idx=0, output_color="BGR")
        self._window_id = window_id

    def start(self, target_fps: int = 30) -> None:
        self._camera.start(target_fps=target_fps, video_mode=True)

    def get_latest(self) -> Any:
        return self._camera.get_latest_frame()

    def stop(self) -> None:
        self._camera.stop()


class WindowsInputAdapter:
    """Minimal SendInput executor; callers must pass actions through the Arbiter."""

    def __init__(self, window_id: int) -> None:
        require_windows()
        self._window_id = window_id

    def dispatch(self, action: ActionProposal) -> None:
        require_windows()
        if action.action_type is ActionType.WAIT:
            return
        if action.action_type in (ActionType.KEY_DOWN, ActionType.KEY_UP):
            self._send_key(action.key, action.action_type is ActionType.KEY_UP)
            return
        if action.action_type in (ActionType.MOUSE_DOWN, ActionType.MOUSE_UP):
            self._send_mouse_button(action.button, action.action_type is ActionType.MOUSE_UP)
            return
        if action.action_type is ActionType.MOUSE_MOVE:
            self._send_mouse_move(action.x, action.y)
            return
        raise ValueError(f"unsupported action type: {action.action_type}")

    def release_all(self) -> None:
        require_windows()
        # The Arbiter tracks exact held inputs; this adapter's release-all is a
        # safety fallback for platform teardown.
        for key in ("shift", "ctrl", "alt", "space", "enter"):
            self._send_key(key, key_up=True)
        for button in MouseButton:
            self._send_mouse_button(button, button_up=True)

    @staticmethod
    def _send_key(key: str | None, key_up: bool) -> None:
        if key is None:
            raise ValueError("key is required")
        vk = _VIRTUAL_KEYS.get(key)
        if vk is None:
            raise ValueError(f"unsupported Windows virtual key: {key}")
        flags = 0x0002 if key_up else 0
        _send_input(_KeyboardInput(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=None))

    @staticmethod
    def _send_mouse_button(button: MouseButton | None, button_up: bool) -> None:
        flags = {
            MouseButton.LEFT: (0x0002, 0x0004),
            MouseButton.RIGHT: (0x0008, 0x0010),
            MouseButton.MIDDLE: (0x0020, 0x0040),
        }
        if button not in flags:
            raise ValueError("mouse button is required")
        _send_input(
            _MouseInput(
                dx=0,
                dy=0,
                mouseData=0,
                dwFlags=flags[button][1 if button_up else 0],
                time=0,
                dwExtraInfo=None,
            )
        )

    @staticmethod
    def _send_mouse_move(x: int | None, y: int | None) -> None:
        if x is None or y is None:
            raise ValueError("mouse coordinates are required")
        _send_input(
            _MouseInput(
                dx=x,
                dy=y,
                mouseData=0,
                dwFlags=0x0001,
                time=0,
                dwExtraInfo=None,
            )
        )


_VIRTUAL_KEYS = {
    **{chr(code): code for code in range(ord("A"), ord("Z") + 1)},
    **{str(code - ord("0")): code for code in range(ord("0"), ord("9") + 1)},
    "enter": 0x0D,
    "escape": 0x1B,
    "space": 0x20,
    "tab": 0x09,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "up": 0x26,
    "down": 0x28,
    "left": 0x25,
    "right": 0x27,
}


class _KeyboardInput(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class _MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


def _send_input(payload: _KeyboardInput | _MouseInput) -> None:
    if sys.platform != "win32":
        raise RuntimeError("SendInput is available only on Windows")
    class _InputUnion(ctypes.Union):
        _fields_ = [("ki", _KeyboardInput), ("mi", _MouseInput)]

    class _Input(ctypes.Structure):
        _anonymous_ = ("union",)
        _fields_ = [("type", wintypes.DWORD), ("union", _InputUnion)]

    if isinstance(payload, _KeyboardInput):
        native_input = _Input(type=1, ki=payload)
    else:
        native_input = _Input(type=0, mi=payload)
    sent = ctypes.windll.user32.SendInput(1, ctypes.byref(native_input), ctypes.sizeof(_Input))
    if sent != 1:
        raise OSError("Windows SendInput rejected the event")
