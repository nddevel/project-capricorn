"""
model_client.py
Communicates with local Ollama service via HTTP REST API.
Runs inference in a non-blocking background thread.
"""

import json
import threading
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "capri:latest"


class OllamaClient:
    """
    Sends messages to Ollama and streams the reply token-by-token
    via callbacks to update the PySide6 UI smoothly.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._history: List[Dict[str, str]] = []
        self._lock = threading.Lock()

    def send(
        self,
        user_message: str,
        on_token: Callable[[str], None],
        on_done: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        """
        Non-blocking call. Spawns a background thread to call Ollama.
        """
        thread = threading.Thread(
            target=self._stream,
            args=(user_message, on_token, on_done, on_error),
            daemon=True,
        )
        thread.start()

    def clear_history(self) -> None:
        """Resets the conversation context."""
        with self._lock:
            self._history.clear()

    def is_connected(self) -> bool:
        """Pings Ollama daemon to check connectivity."""
        try:
            req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
            return req.status == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """Returns list of installed Ollama models."""
        try:
            req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
            if req.status == 200:
                data = json.loads(req.read().decode())
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def _stream(
        self,
        user_message: str,
        on_token: Callable[[str], None],
        on_done: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        with self._lock:
            messages = list(self._history) + [{"role": "user", "content": user_message}]

        payload = json.dumps(
            {
                "model": self.model_name,
                "messages": messages,
                "stream": True,
            }
        ).encode("utf-8")

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            full_reply = ""

            with urllib.request.urlopen(req, timeout=120) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    chunk = obj.get("message", {}).get("content", "")
                    if chunk:
                        full_reply += chunk
                        on_token(chunk)

                    if obj.get("done"):
                        break

            with self._lock:
                self._history.extend(
                    [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": full_reply},
                    ]
                )

            on_done(full_reply)

        except urllib.error.URLError:
            on_error(
                "// CONNECTION LOST — is Ollama service running on localhost:11434?"
            )
        except Exception as e:
            on_error(f"// ERROR: {e}")
