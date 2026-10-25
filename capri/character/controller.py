"""
controller.py
Manages Capri's animation states and resolves active image frame filepaths.
"""

import os
from enum import Enum, auto
from typing import Callable, Optional


class CapriState(Enum):
    IDLE = auto()
    HAPPY = auto()
    BLINK = auto()
    SLEEPING = auto()


STATE_IMAGES = {
    CapriState.IDLE: "capri_idle.png",
    CapriState.HAPPY: "capri_happy.png",
    CapriState.BLINK: "capri_blink.png",
    CapriState.SLEEPING: "capri_sleeping.png",
}

FALLBACK_ORDER = [
    CapriState.IDLE,
    CapriState.BLINK,
    CapriState.HAPPY,
    CapriState.SLEEPING,
]


class CharacterController:
    """
    Tracks state and notifies listener window of image changes.
    """

    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self._state = CapriState.IDLE
        self._on_change: Optional[Callable[[str], None]] = None

    def set_state(self, state: CapriState) -> None:
        """Updates Capri's state and triggers UI image update."""
        if state != self._state:
            self._state = state
            if self._on_change:
                self._on_change(self.current_image_path())

    def current_state(self) -> CapriState:
        return self._state

    def current_image_path(self) -> str:
        """Resolves file path for current state or fallback."""
        path = self._resolve_path(self._state)
        if path:
            return path

        for fallback in FALLBACK_ORDER:
            path = self._resolve_path(fallback)
            if path:
                return path

        return ""

    def register_change_callback(self, fn: Callable[[str], None]) -> None:
        """Registers window update callback."""
        self._on_change = fn

    def _resolve_path(self, state: CapriState) -> str:
        filename = STATE_IMAGES.get(state, "")
        if not filename:
            return ""
        full = os.path.join(self.assets_dir, filename)
        return full if os.path.isfile(full) else ""
