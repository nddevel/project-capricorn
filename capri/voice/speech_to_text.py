"""
speech_to_text.py
Speech recognition using faster-whisper on CPU.
"""

import threading

import numpy as np

try:
    import sounddevice as sd
    import soundfile as sf
    from faster_whisper import WhisperModel

    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

SAMPLE_RATE = 16000
CHANNELS = 1
MODEL_SIZE = "base"
COMPUTE_TYPE = "int8"
DEVICE = "cpu"
MIN_SECONDS = 0.3
SILENCE_DB = -40


class SpeechToText:
    def __init__(self):
        self._model = None
        self._frames: list[np.ndarray] = []
        self._recording = False
        self._lock = threading.Lock()
        self._stream = None

        if STT_AVAILABLE:
            threading.Thread(target=self._load_model, daemon=True).start()

    def is_ready(self) -> bool:
        return STT_AVAILABLE and self._model is not None

    def start_recording(self) -> None:
        if not STT_AVAILABLE:
            return
        with self._lock:
            if self._recording:
                return
            self._frames = []
            self._recording = True
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="float32",
                callback=self._audio_callback,
            )
            self._stream.start()
        except Exception as e:
            print(f"[STT] Could not start audio stream: {e}")
            self._recording = False

    def stop_and_transcribe(self) -> str:
        if not STT_AVAILABLE:
            return ""

        with self._lock:
            self._recording = False

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        if not self._frames:
            return ""

        audio = np.concatenate(self._frames, axis=0).flatten()
        if len(audio) < SAMPLE_RATE * MIN_SECONDS:
            return ""

        rms_db = 20 * np.log10(np.sqrt(np.mean(audio**2)) + 1e-9)
        if rms_db < SILENCE_DB:
            return ""

        return self._transcribe(audio)

    def _load_model(self) -> None:
        try:
            print(f"[STT] Loading Whisper {MODEL_SIZE} on {DEVICE}...")
            self._model = WhisperModel(
                MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE
            )
            print("[STT] Whisper engine initialized.")
        except Exception as e:
            print(f"[STT] Model load failed: {e}")

    def _audio_callback(self, indata, frames, time, status) -> None:
        with self._lock:
            if self._recording:
                self._frames.append(indata.copy())

    def _transcribe(self, audio: np.ndarray) -> str:
        if self._model is None:
            return ""
        try:
            segments, _ = self._model.transcribe(
                audio,
                language="en",
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 300},
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            if text:
                print(f"[STT] Recognized: {text!r}")
            return text
        except Exception as e:
            print(f"[STT] Transcription error: {e}")
            return ""
