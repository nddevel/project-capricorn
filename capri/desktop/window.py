"""
window.py
Frameless, transparent desktop mascot window for GNOME / Linux Desktop.
"""

import random
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from capri.character.controller import CapriState, CharacterController

WINDOW_SIZE = QSize(200, 200)
BLINK_INTERVAL_MS = 4000
BLINK_HOLD_MS = 150
HAPPY_HOLD_MS = 1200
SLEEP_AFTER_MS = 60000


class CapriWindow(QWidget):
    """
    Transparent, borderless, always-on-top PySide6 mascot window.
    """

    def __init__(self, controller: CharacterController):
        super().__init__()
        self.controller = controller
        self._drag_start_pos: QPoint | None = None
        self._press_global_pos: QPoint | None = None
        self._chat_window = None
        self._is_sleeping = False

        self._idle_frames = []
        for filename in ("capri_idle1.png", "capri_idle2.png", "capri_idle3.png"):
            image_path = Path(self.controller.assets_dir) / filename
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self._idle_frames.append(pixmap)

        self._idle_frame_index = 0

        self._sleeping_frames = []
        for filename in (
            "capri_sleeping0.png",
            "capri_sleeping1.png",
            "capri_sleeping2.png",
        ):
            image_path = Path(self.controller.assets_dir) / filename
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self._sleeping_frames.append(pixmap)

        self._sleeping_frame_index = 0

        self._setup_window()
        self._setup_ui()
        self._setup_timers()

        self.controller.register_change_callback(self._update_image)
        self._update_image(self.controller.current_image_path())

    def set_chat_window(self, chat_window) -> None:
        self._chat_window = chat_window

    def _toggle_chat(self) -> None:
        if self._chat_window is None:
            return
        if self._chat_window.isVisible():
            self._chat_window.hide()
        else:
            self._chat_window.show()
            self._chat_window.raise_()
            self._chat_window.activateWindow()
        self._reset_sleep_timer()

    def _setup_window(self) -> None:
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setFixedSize(WINDOW_SIZE)

        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() - WINDOW_SIZE.width() - 50,
            screen.height() - WINDOW_SIZE.height() - 80,
        )

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.image_label)

    def _setup_timers(self) -> None:
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._do_blink)
        self._schedule_next_blink()

        self._blink_reset = QTimer(self)
        self._blink_reset.setSingleShot(True)
        self._blink_reset.timeout.connect(self._end_blink)

        self._happy_reset = QTimer(self)
        self._happy_reset.setSingleShot(True)
        self._happy_reset.timeout.connect(self._end_happy)

        self._sleep_timer = QTimer(self)
        self._sleep_timer.setSingleShot(True)
        self._sleep_timer.timeout.connect(self._go_to_sleep)
        self._sleep_timer.start(SLEEP_AFTER_MS)

        self._sleeping_timer = QTimer(self)
        self._sleeping_timer.timeout.connect(self._animate_sleeping)
        self._sleeping_timer.start(350)

        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._animate_idle)
        self._idle_timer.start(160)

    def _update_image(self, path: str) -> None:
        if self._is_sleeping and self._sleeping_frames:
            self._sleeping_frame_index = 0
            pixmap = self._sleeping_frames[0].scaled(
                WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            return

        if self.controller.current_state() == CapriState.IDLE and self._idle_frames:
            self._idle_frame_index = 0
            pixmap = self._idle_frames[0].scaled(
                WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            return

        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.image_label.setPixmap(pixmap)
                return

        self._draw_placeholder()

    def _animate_sleeping(self) -> None:
        if not self._is_sleeping or not self._sleeping_frames:
            return
        self._sleeping_frame_index = (self._sleeping_frame_index + 1) % len(
            self._sleeping_frames
        )
        pixmap = self._sleeping_frames[self._sleeping_frame_index].scaled(
            WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def _animate_idle(self) -> None:
        if (
            self._is_sleeping
            or self.controller.current_state() != CapriState.IDLE
            or not self._idle_frames
        ):
            return
        self._idle_frame_index = (self._idle_frame_index + 1) % len(self._idle_frames)
        pixmap = self._idle_frames[self._idle_frame_index].scaled(
            WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def _draw_placeholder(self) -> None:
        placeholder = QPixmap(WINDOW_SIZE)
        placeholder.fill(QColor(0, 0, 0, 0))

        painter = QPainter(placeholder)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor("#00e5ff"), 3))
        painter.setBrush(QColor(10, 15, 30, 220))
        painter.drawEllipse(40, 40, 120, 120)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#ff2d78"))
        painter.drawEllipse(70, 85, 20, 20)
        painter.drawEllipse(110, 85, 20, 20)

        painter.setPen(QColor("#f5e642"))
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        painter.drawText(0, 175, WINDOW_SIZE.width(), 20, Qt.AlignHCenter, "CAPRI")
        painter.end()

        self.image_label.setPixmap(placeholder)

    def _schedule_next_blink(self) -> None:
        jitter = random.randint(-800, 800)
        self._blink_timer.start(BLINK_INTERVAL_MS + jitter)

    def _do_blink(self) -> None:
        if self._is_sleeping:
            return
        self.controller.set_state(CapriState.BLINK)
        self._blink_reset.start(BLINK_HOLD_MS)
        self._schedule_next_blink()

    def _end_blink(self) -> None:
        if self.controller.current_state() == CapriState.BLINK:
            self.controller.set_state(CapriState.IDLE)

    def _end_happy(self) -> None:
        if self.controller.current_state() == CapriState.HAPPY:
            self.controller.set_state(CapriState.IDLE)

    def _go_to_sleep(self) -> None:
        self._is_sleeping = True
        self._blink_timer.stop()
        self.controller.set_state(CapriState.SLEEPING)

    def _wake_up(self) -> None:
        self._is_sleeping = False
        self.controller.set_state(CapriState.HAPPY)
        self._happy_reset.start(HAPPY_HOLD_MS)
        self._schedule_next_blink()
        self._reset_sleep_timer()

    def _reset_sleep_timer(self) -> None:
        self._sleep_timer.start(SLEEP_AFTER_MS)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._press_global_pos = event.globalPosition().toPoint()
            self._drag_start_pos = event.globalPosition().toPoint() - self.pos()
            if self._is_sleeping:
                self._wake_up()
            else:
                self._reset_sleep_timer()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_start_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            release_pos = event.globalPosition().toPoint()
            was_click = (
                self._press_global_pos is not None
                and (release_pos - self._press_global_pos).manhattanLength()
                < QApplication.startDragDistance()
            )
            self._drag_start_pos = None
            self._press_global_pos = None
            if was_click and not self._is_sleeping:
                self._toggle_chat()

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and not self._is_sleeping:
            self.controller.set_state(CapriState.HAPPY)
            self._happy_reset.start(HAPPY_HOLD_MS)
            self._reset_sleep_timer()

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #08080f;
                border: 1px solid #00e5ff;
                color: #c8f0f5;
                font-family: monospace;
                font-size: 11px;
                padding: 4px;
            }
            QMenu::item:selected { background: #ff2d78; color: #000; }
        """)

        if self._is_sleeping:
            wake = menu.addAction("⚡ Wake Capri")
            wake.triggered.connect(self._wake_up)
        else:
            sleep = menu.addAction("💤 Sleep")
            sleep.triggered.connect(self._go_to_sleep)

        menu.addSeparator()
        quit_action = menu.addAction("✕ Quit")
        quit_action.triggered.connect(QApplication.quit)
        menu.exec(event.globalPos())

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        super().paintEvent(event)
