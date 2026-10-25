"""
main.py
Application entry point for Capri on GNOME / Linux Desktop.
"""

import os
import sys

from PySide6.QtWidgets import QApplication

from capri.ai.model_client import OllamaClient
from capri.character.controller import CharacterController
from capri.desktop.chat_window import ChatWindow
from capri.desktop.window import CapriWindow


def get_assets_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    return os.path.join(root, "assets", "character")


def load_voice_components():
    """
    Attempts to initialize voice components (STT/TTS/PTT).
    If dependencies or hardware models are missing, returns (None, None, None)
    so Capri gracefully falls back to text-only terminal mode.
    """
    try:
        from capri.voice.ptt import PushToTalk
        from capri.voice.speech_to_text import SpeechToText
        from capri.voice.text_to_speech import TextToSpeech

        tts = TextToSpeech()
        stt = SpeechToText()
        ptt = PushToTalk(on_press=lambda: None, on_release=lambda: None)

        if not tts.is_available():
            print("[Voice] Piper TTS or spd-say not found. Running text-only mode.")
            return None, None, None

        print("[Voice] Engine initialized. Hold LEFT CTRL to speak.")
        return stt, tts, ptt

    except Exception as e:
        print(f"[Voice] Voice setup info: {e}. Running text-only mode.")
        return None, None, None


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Capri")
    app.setQuitOnLastWindowClosed(False)

    assets_dir = get_assets_dir()
    controller = CharacterController(assets_dir)
    ai_client = OllamaClient()

    stt, tts, ptt = load_voice_components()

    capri_win = CapriWindow(controller)
    chat_win = ChatWindow(ai_client, controller, capri_win, stt=stt, tts=tts, ptt=ptt)

    capri_win.set_chat_window(chat_win)
    capri_win.show()

    print("==================================================")
    print("  Capri Cyberpunk Companion (GNOME / Linux)      ")
    print("==================================================")
    print("  - Left-click Capri to open/close chat terminal  ")
    print("  - Drag Capri anywhere on screen                ")
    print("  - Double-click to poke her                     ")
    print("  - Right-click for context menu                 ")
    print("==================================================")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
