"""
ptt.py
Global Push-To-Talk hook for Linux GNOME Desktop.
Hold LEFT CTRL to record, release to transcribe.
"""

import threading
from typing import Callable

try:
    from pynput import keyboard

    PTT_KEY = keyboard.Key.ctrl_l
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class PushToTalk:
    def __init__(self, on_press: Callable[[], None], on_release: Callable[[], None]):
        self._on_press = on_press
        self._on_release = on_release
        self._held = False
        self._listener = None

    def start(self) -> None:
        if not PYNPUT_AVAILABLE:
            print("[PTT] pynput library not found — voice input disabled.")
            return

        try:
            self._listener = keyboard.Listener(
                on_press=self._handle_press,
                on_release=self._handle_release,
            )
            self._listener.daemon = True
            self._listener.start()
            print("[PTT] Active — hold LEFT CTRL to speak.")
        except Exception as e:
            print(f"[PTT] Could not start keyboard listener: {e}")

    def stop(self) -> None:
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass

    def _handle_press(self, key) -> None:
        if PYNPUT_AVAILABLE and key == PTT_KEY and not self._held:
            self._held = True
            threading.Thread(target=self._on_press, daemon=True).start()

    def _handle_release(self, key) -> None:
        if PYNPUT_AVAILABLE and key == PTT_KEY and self._held:
            self._held = False
            threading.Thread(target=self._on_release, daemon=True).start()
