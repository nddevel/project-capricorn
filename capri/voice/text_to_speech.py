"""
text_to_speech.py
Linux TTS engine support (Piper binary, spd-say, or silent text mode).
"""

import os
import shutil
import subprocess
import tempfile
import threading

try:
    import sounddevice as sd
    import soundfile as sf

    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


def find_piper_executable() -> str:
    """Finds piper binary in PATH or common Linux locations."""
    in_path = shutil.which("piper")
    if in_path:
        return in_path

    user_bin = os.path.expanduser("~/.local/bin/piper")
    if os.path.isfile(user_bin) and os.access(user_bin, os.X_OK):
        return user_bin

    usr_bin = "/usr/bin/piper"
    if os.path.isfile(usr_bin) and os.access(usr_bin, os.X_OK):
        return usr_bin

    return ""


PIPER_EXE = find_piper_executable()
VOICE_MODEL = os.path.expanduser("~/.local/share/piper/en_US-libritts-high.onnx")


class TextToSpeech:
    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def is_available(self) -> bool:
        if PIPER_EXE and os.path.isfile(VOICE_MODEL):
            return True
        return shutil.which("spd-say") is not None

    def speak(self, text: str, on_done: callable = None) -> None:
        self.stop()
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, args=(text, on_done), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if AUDIO_AVAILABLE:
            try:
                sd.stop()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

    def is_speaking(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self, text: str, on_done: callable) -> None:
        if PIPER_EXE and os.path.isfile(VOICE_MODEL) and AUDIO_AVAILABLE:
            self._run_piper(text)
        elif shutil.which("spd-say"):
            self._run_spdsay(text)

        if on_done and not self._stop.is_set():
            on_done()

    def _run_piper(self, text: str) -> None:
        tmp = None
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()

            proc = subprocess.run(
                [PIPER_EXE, "--model", VOICE_MODEL, "--output_file", tmp.name],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=20,
            )

            if proc.returncode != 0 or self._stop.is_set():
                return

            data, sr = sf.read(tmp.name)
            sd.play(data, sr)

            while sd.get_stream().active:
                if self._stop.is_set():
                    sd.stop()
                    return
                threading.Event().wait(0.05)

            sd.wait()

        except Exception as e:
            print(f"[TTS] Piper error: {e}")
        finally:
            if tmp and os.path.exists(tmp.name):
                try:
                    os.unlink(tmp.name)
                except Exception:
                    pass

    def _run_spdsay(self, text: str) -> None:
        try:
            subprocess.run(["spd-say", "-r", "10", text], timeout=10)
        except Exception:
            pass
