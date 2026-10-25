#!/usr/bin/env bash

# Capri Launcher for GNOME / Linux / NixOS Desktop
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo " Starting Capri Desktop Companion on Linux...    "
echo "=================================================="

# Detect NixOS / FHS wrapper if needed
RUNNER=""
if command -v steam-run &>/dev/null; then
    RUNNER="steam-run"
fi

# Set up virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "[Init] Creating Python virtual environment in .venv..."
    if command -v python3 &>/dev/null; then
        python3 -m venv .venv
    else
        python -m venv .venv
    fi
fi

VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
VENV_PIP="$SCRIPT_DIR/.venv/bin/pip"

# Install requirements if PySide6 isn't present
if ! $RUNNER "$VENV_PYTHON" -c "import PySide6" &>/dev/null; then
    echo "[Setup] Installing PySide6 and desktop dependencies..."
    $RUNNER "$VENV_PIP" install --upgrade pip setuptools wheel
    $RUNNER "$VENV_PIP" install evdev-binary 2>/dev/null || true
    $RUNNER "$VENV_PIP" install -r requirements.txt || $RUNNER "$VENV_PIP" install PySide6
fi

# Check Ollama status
if command -v ollama &>/dev/null; then
    if curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo "[Ollama] Connected to local Ollama service on port 11434."
    else
        echo "[Ollama] Starting background service..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
    fi

    # Create capri model if not present
    if ! ollama list 2>/dev/null | grep -q "capri"; then
        echo "[Ollama] Creating custom 'capri' model from Modelfile..."
        ollama create capri -f "$SCRIPT_DIR/Modelfile" || echo "[Warning] Failed to create capri model."
    fi
else
    echo "[Notice] 'ollama' binary not in PATH. Ensure Ollama is running on http://localhost:11434"
fi

# Launch Capri
echo "[Launch] Starting Capri GUI..."
if [ -n "$RUNNER" ]; then
    $RUNNER "$VENV_PYTHON" -m capri.main
else
    "$VENV_PYTHON" -m capri.main
fi
