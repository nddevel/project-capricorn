# Capri — Cyberpunk Desktop Companion (Linux / GNOME)

> A lightweight, Cyberpunk 2077 inspired animated desktop pet and local AI companion for Linux / GNOME Desktop.

Capri lives directly on your desktop as an animated character with interactive states, drag-and-drop movement, and a terminal-style chat window powered locally by **Ollama** and **Gemma 2**.

---

## ✨ Features

- **🎮 GNOME Desktop Pet Mascot:**
  - Frameless, borderless, transparent PySide6 widget.
  - Stays on top of windows or runs unobtrusively on your desktop.
  - Full mouse controls: Left-click + drag to move, double-click to poke, right-click for context menu.

- **🎭 Animated Character States:**
  - **Idle Animation:** Multi-frame continuous idle loop.
  - **Blinking:** Natural eye blinking with random time jitter.
  - **Happy Reaction:** Expression triggered when interacted with or poked.
  - **Sleeping Mode:** Enters a sleeping state after inactivity or via right-click menu, and wakes up when clicked.

- **💻 Cyberpunk Terminal Chat UI (`CAPRI // TERMINAL`):**
  - Neon monospace styling (`#08080f` background, `#00e5ff` cyan highlights, `#f5e642` yellow prompts).
  - Real-time token streaming from local Ollama model.
  - Status indicators (`CONNECTED`, `THINKING`, `OFFLINE`).

- **🤖 100% Local AI (Privacy First):**
  - Powered by Ollama via HTTP REST API (`http://localhost:11434`).
  - Custom persona defined in `Modelfile` (Relaxed, witty, cyberpunk personality).

- **🎤 Voice Interactions (Optional):**
  - **Push-to-Talk (PTT):** Hold `Left Ctrl` to speak.
  - **Speech-to-Text (STT):** Local CPU speech recognition using `faster-whisper`.
  - **Text-to-Speech (TTS):** Spoken replies via local `Piper` TTS or `spd-say`.

- **🐧 Linux & NixOS Ready:**
  - Built-in `run.sh` launcher script with virtual environment auto-setup.
  - Automatic `steam-run` FHS wrapper detection for NixOS compatibility.
  - `capri.desktop` application shortcut included.

---

## 🚀 Getting Started

### 1. Prerequisites

- Linux Desktop (GNOME, X11, or Wayland)
- Python 3.10+
- [Ollama](https://ollama.com) installed and running

#### Install & Start Ollama on Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

### 2. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/Capri-Desktop-Companion.git
cd Capri-Desktop-Companion
```

### 3. Create Custom Ollama Model

Create Capri's model using the provided `Modelfile`:
```bash
ollama create capri -f ./Modelfile
```

### 4. Launch Capri

Run the launcher script (automatically creates `.venv` and installs dependencies):
```bash
chmod +x run.sh
./run.sh
```

---

## 🎮 Mascot Controls

| Action | Control |
|---|---|
| **Toggle Chat Terminal** | Left-Click Mascot |
| **Move Mascot** | Left-Click + Drag |
| **Poke Mascot** | Double Left-Click |
| **Context Menu** | Right-Click Mascot (Sleep / Wake / Quit) |
| **Push-to-Talk (Voice)** | Hold `Left Ctrl` |
| **Stop Speech Playback** | Press `ESC` in Chat |

---

## 📁 Project Layout

```
capri/
├── Modelfile                  # Ollama personality definition & directives
├── requirements.txt           # Python PySide6, audio & input dependencies
├── run.sh                     # Smart Linux launcher script
├── capri.desktop              # GNOME Application menu desktop shortcut
├── LICENSE                    # MIT License
├── README.md                  # Project documentation
├── assets/
│   ├── character/             # Idle frames, blink, happy, and sleeping sprites
│   └── ui/                    # Terminal icons and UI artwork
└── capri/
    ├── __init__.py
    ├── main.py                # Main application entry point
    ├── ai/
    │   └── model_client.py    # Ollama REST API streaming client
    ├── character/
    │   └── controller.py      # Mascot state machine & animation controller
    ├── desktop/
    │   ├── window.py          # PySide6 transparent desktop mascot widget
    │   └── chat_window.py     # Cyberpunk terminal GUI window
    └── voice/
        ├── ptt.py             # Push-to-talk listener
        ├── speech_to_text.py  # Faster-Whisper audio transcription
        └── text_to_speech.py  # Piper/Linux text-to-speech engine
```

---

## 🧠 Customizing Capri's Personality

You can adjust Capri's tone, knowledge, and demeanor by editing the `SYSTEM` instructions in `Modelfile`.

After editing `Modelfile`, rebuild the model:
```bash
ollama create capri -f ./Modelfile
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
