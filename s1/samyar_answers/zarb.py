"""
تمرین ضرب — Multiplication Trainer
PySide6 desktop app, iOS "Liquid Glass" inspired, orange premium theme.

Run:
    pip install PySide6
    python main.py
"""

import sys
import random

from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QVariantAnimation, QEasingCurve,
    QRectF, Signal, QAbstractAnimation
)
from PySide6.QtGui import (
    QColor, QFont, QIntValidator, QLinearGradient, QPainter, QBrush
)
from PySide6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget, QGraphicsOpacityEffect
)


# ---------- Helpers ----------
def normalize_fa_numbers(text: str) -> str:
    """تبدیل اعداد فارسی و عربی به اعداد انگلیسی standard"""
    translation_table = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    return text.translate(translation_table)


# ---------- Palette ----------
ORANGE = "255, 138, 0"
ORANGE_DEEP = "#F57C00"
TEXT_DARK = "#3A2000"
TEXT_MUTED = "#8A6A42"
WARN_RED = "#D32F2F"

INPUT_STYLE = f"""
    QLineEdit {{
        background-color: rgba(255, 255, 255, 0.85);
        border: 2px solid rgba({ORANGE}, 0.35);
        border-radius: 22px;
        padding: 6px 16px;
        color: {TEXT_DARK};
        selection-background-color: rgba({ORANGE}, 0.35);
    }}
    QLineEdit:focus {{
        border: 2px solid rgba({ORANGE}, 0.95);
        background-color: rgba(255, 255, 255, 0.98);
    }}
"""


# ---------- Background ----------
class GradientBackground(QWidget):
    """Soft orange gradient with gentle decorative blobs."""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        grad = QLinearGradient(0, 0, r.width(), r.height())
        grad.setColorAt(0.0, QColor("#FFF8F0"))
        grad.setColorAt(0.45, QColor("#FFE9D2"))
        grad.setColorAt(1.0, QColor("#FFD2A0"))
        p.fillRect(r, QBrush(grad))

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 138, 0, 45))
        p.drawEllipse(QRectF(-160, -180, 420, 420))

        p.setBrush(QColor(245, 124, 0, 40))
        p.drawEllipse(QRectF(r.width() - 300, r.height() - 260, 460, 460))

        p.setBrush(QColor(255, 183, 77, 55))
        p.drawEllipse(QRectF(r.width() * 0.55, 30, 300, 300))


# ---------- Glass card ----------
class GlassCard(QFrame):
    """Frosted glass panel: translucent white, subtle border, soft shadow."""

    def __init__(self, radius=32, parent=None):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#glassCard {{
                background-color: rgba(255, 255, 255, 0.62);
                border: 1px solid rgba(255, 255, 255, 0.85);
                border-radius: {radius}px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(42)
        shadow.setColor(QColor(190, 105, 20, 85))
        shadow.setOffset(0, 12)
        self.setGraphicsEffect(shadow)


# ---------- Glass button ----------
class GlassButton(QPushButton):
    """Liquid-glass style button with smooth hover feedback."""

    def __init__(self, text="", primary=True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._hover = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(58)
        self.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._apply_style()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(255, 120, 0, 150))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)

    def _apply_style(self):
        if self.primary:
            bg = f"rgba({ORANGE}, {'1.0' if self._hover else '0.92'})"
            color = "#FFFFFF"
        else:
            bg = f"rgba(255, 255, 255, {'0.9' if self._hover else '0.65'})"
            color = ORANGE_DEEP

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: 1px solid rgba(255, 255, 255, 0.9);
                border-radius: 22px;
                padding: 10px 28px;
            }}
            QPushButton:pressed {{
                padding-top: 12px;
                padding-bottom: 8px;
            }}
        """)

    def enterEvent(self, e):
        self._hover = True
        self._apply_style()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self._apply_style()
        super().leaveEvent(e)


# ---------- Start page ----------
class StartPage(QWidget):
    start_clicked = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addStretch(1)

        card = GlassCard(radius=36)
        card.setMaximumWidth(460)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(42, 54, 42, 54)
        card_layout.setSpacing(16)

        title = QLabel("تمرین ضرب")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 34, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
        card_layout.addWidget(title)

        sub = QLabel("آماده‌ای برای تمرین سریع؟")
        sub.setAlignment(Qt.AlignCenter)
        sub.setFont(QFont("Segoe UI", 14))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        card_layout.addWidget(sub)

        card_layout.addSpacing(22)

        btn = GlassButton("شروع بازی")
        btn.clicked.connect(self.start_clicked.emit)
        card_layout.addWidget(btn)

        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(card)
        wrap.addStretch(1)

        layout.addLayout(wrap)
        layout.addStretch(1)


# ---------- Game page ----------
class GamePage(QWidget):
    answer_submitted = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Stats row
        stats = QHBoxLayout()
        stats.setSpacing(12)

        self.score_card = self._make_stat_card("امتیاز", "0")
        self.record_card = self._make_stat_card("رکورد پاسخ‌های درست", "0")

        stats.addWidget(self.score_card["frame"], 1)
        stats.addWidget(self.record_card["frame"], 1)

        layout.addLayout(stats)

        # Main card
        card = GlassCard(radius=36)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 38, 36, 38)
        card_layout.setSpacing(18)

        self.timer_label = QLabel("10.0")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFont(QFont("Consolas", 22, QFont.Bold))
        self.timer_label.setFixedHeight(34)
        self.timer_label.setStyleSheet(
            f"color: {ORANGE_DEEP}; background: transparent;"
        )
        card_layout.addWidget(self.timer_label)

        self.question_label = QLabel("7 × 8")
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Segoe UI", 56, QFont.Bold))
        self.question_label.setFixedHeight(104)
        self.question_label.setStyleSheet(
            f"color: {TEXT_DARK}; background: transparent;"
        )
        card_layout.addWidget(self.question_label)

        self.input = QLineEdit()
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.input.setPlaceholderText("؟")
        self.input.setValidator(QIntValidator(0, 9999, self))
        self.input.setFixedHeight(78)
        self.input.setStyleSheet(INPUT_STYLE)
        self.input.returnPressed.connect(self._submit)
        card_layout.addWidget(self.input)

        layout.addWidget(card)

        hint = QLabel("پاسخ را وارد کن و Enter بزن")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Segoe UI", 11))
        hint.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        layout.addWidget(hint)

    # -- helpers --
    def _make_stat_card(self, title, value):
        frame = GlassCard(radius=22)
        v = QVBoxLayout(frame)
        v.setContentsMargins(18, 12, 18, 12)
        v.setSpacing(2)

        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Segoe UI", 10))
        t.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        val = QLabel(value)
        val.setAlignment(Qt.AlignCenter)
        val.setFont(QFont("Segoe UI", 20, QFont.Bold))
        val.setStyleSheet(f"color: {ORANGE_DEEP}; background: transparent;")

        v.addWidget(t)
        v.addWidget(val)

        return {"frame": frame, "title": t, "value": val}

    def _submit(self):
        clean_text = normalize_fa_numbers(self.input.text())
        self.answer_submitted.emit(clean_text)

    # -- public API --
    def set_score(self, s):
        self.score_card["value"].setText(str(s))
        self._pulse(self.score_card["value"], 20)

    def set_record(self, s):
        self.record_card["value"].setText(str(s))

    def set_question(self, text):
        self.question_label.setText(text)

    def set_timer(self, value, normal=True):
        self.timer_label.setText(f"{value:.1f}")
        color = ORANGE_DEEP if normal else WARN_RED
        self.timer_label.setStyleSheet(
            f"color: {color}; background: transparent;"
        )

    def clear_input(self):
        self.input.clear()

    def focus_input(self):
        self.input.setFocus()
        self.input.activateWindow()

    def disable_input(self):
        self.input.setEnabled(False)

    def enable_input(self):
        self.input.setEnabled(True)

    def _pulse(self, label, base_size):
        anim = QVariantAnimation(self)
        anim.setDuration(280)
        anim.setStartValue(float(base_size))
        anim.setKeyValueAt(0.45, float(base_size) * 1.4)
        anim.setEndValue(float(base_size))
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def on_val(v):
            size = max(10, int(round(float(v))))
            label.setFont(QFont("Segoe UI", size, QFont.Bold))

        anim.valueChanged.connect(on_val)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def animate_question(self):
        label = self.question_label

        anim = QVariantAnimation(self)
        anim.setDuration(350)
        anim.setStartValue(38.0)
        anim.setKeyValueAt(0.55, 62.0)
        anim.setEndValue(56.0)
        anim.setEasingCurve(QEasingCurve.OutBack)

        def on_val(v):
            size = max(10, int(round(float(v))))
            label.setFont(QFont("Segoe UI", size, QFont.Bold))

        anim.valueChanged.connect(on_val)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _flash_input(self, color, bg):
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg};
                border: 2px solid {color};
                border-radius: 22px;
                padding: 6px 16px;
                color: {TEXT_DARK};
            }}
        """)
        QTimer.singleShot(320, lambda: self.input.setStyleSheet(INPUT_STYLE))

    def flash_correct(self):
        self._flash_input("rgba(76, 175, 80, 0.95)", "rgba(232, 245, 233, 0.98)")

    def flash_wrong(self):
        self._flash_input("rgba(244, 67, 54, 0.95)", "rgba(255, 235, 238, 0.98)")

    def alert_timeout(self):
        label = self.timer_label
        anim = QVariantAnimation(self)
        anim.setDuration(500)
        anim.setStartValue(22.0)
        anim.setKeyValueAt(0.3, 34.0)
        anim.setKeyValueAt(0.6, 26.0)
        anim.setEndValue(22.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def on_val(v):
            size = max(10, int(round(float(v))))
            label.setFont(QFont("Consolas", size, QFont.Bold))

        anim.valueChanged.connect(on_val)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


# ---------- Result page ----------
class ResultPage(QWidget):
    restart_clicked = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addStretch(1)

        card = GlassCard(radius=36)
        card.setMaximumWidth(460)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(42, 54, 42, 54)
        card_layout.setSpacing(14)

        title = QLabel("بازی تمام شد")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 30, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
        card_layout.addWidget(title)

        card_layout.addSpacing(6)

        self.score_label = QLabel("امتیاز شما: 0")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setFont(QFont("Segoe UI", 19, QFont.Bold))
        self.score_label.setStyleSheet(
            f"color: {ORANGE_DEEP}; background: transparent;"
        )
        card_layout.addWidget(self.score_label)

        self.record_label = QLabel("رکورد: 0")
        self.record_label.setAlignment(Qt.AlignCenter)
        self.record_label.setFont(QFont("Segoe UI", 14))
        self.record_label.setStyleSheet(
            f"color: {TEXT_MUTED}; background: transparent;"
        )
        card_layout.addWidget(self.record_label)

        card_layout.addSpacing(22)

        btn = GlassButton("دوباره شروع کن")
        btn.clicked.connect(self.restart_clicked.emit)
        card_layout.addWidget(btn)

        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(card)
        wrap.addStretch(1)

        layout.addLayout(wrap)
        layout.addStretch(1)

    def set_result(self, score, record):
        self.score_label.setText(f"امتیاز شما: {score}")
        self.record_label.setText(f"رکورد: {record}")


# ---------- Main window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تمرین ضرب")
        self.resize(560, 720)
        self.setMinimumSize(480, 640)

        # Game state
        self.record = 0
        self.score = 0
        self.current_a = 0
        self.current_b = 0
        self.correct_answer = 0
        self.time_left = 10.0
        self.max_time = 10.0
        self.is_running = False
        self.answer_locked = False

        # Countdown timer
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(50)
        self.countdown_timer.timeout.connect(self._tick)

        # Root
        central = GradientBackground()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 24, 24, 24)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack)

        self.start_page = StartPage()
        self.game_page = GamePage()
        self.result_page = ResultPage()

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.game_page)
        self.stack.addWidget(self.result_page)

        # Wire signals
        self.start_page.start_clicked.connect(self.start_game)
        self.result_page.restart_clicked.connect(self.start_game)
        self.game_page.answer_submitted.connect(self._check_answer)

        self.stack.setCurrentWidget(self.start_page)

    # -- game flow --
    def start_game(self):
        self.countdown_timer.stop()
        self.score = 0
        self.is_running = True
        self.answer_locked = False

        self.game_page.set_score(0)
        self.game_page.set_record(self.record)
        self.game_page.enable_input()

        self.stack.setCurrentWidget(self.game_page)
        self._fade_in(self.game_page)

        self._new_question()

    def _get_difficulty_range(self):
        """افزایش درجه سختی متناسب با امتیاز کاربر"""
        if self.score < 5:
            return (2, 9), 10.0
        elif self.score < 12:
            return (3, 12), 8.0
        elif self.score < 20:
            return (4, 15), 6.5
        else:
            return (6, 20), 5.0

    def _new_question(self):
        num_range, time_limit = self._get_difficulty_range()
        self.max_time = time_limit

        self.current_a = random.randint(num_range[0], num_range[1])
        self.current_b = random.randint(num_range[0], num_range[1])
        self.correct_answer = self.current_a * self.current_b

        self.game_page.set_question(f"{self.current_a} × {self.current_b}")
        self.game_page.clear_input()
        self.game_page.enable_input()
        
        # فوکوس دقیق بر روی ورودی با تاخیر کم
        QTimer.singleShot(50, self.game_page.focus_input)

        self.time_left = self.max_time
        self.game_page.set_timer(self.max_time, normal=True)
        self.game_page.animate_question()

        self.answer_locked = False
        self.countdown_timer.stop()
        self.countdown_timer.start()

    def _tick(self):
        if not self.is_running or self.answer_locked:
            return

        self.time_left -= 0.05
        if self.time_left <= 0.0:
            self.time_left = 0.0
            self.game_page.set_timer(0.0, normal=False)
            self.countdown_timer.stop()
            self._lose_game("timeout")
            return

        self.game_page.set_timer(self.time_left, normal=self.time_left > (self.max_time * 0.3))

    def _check_answer(self, text):
        if not self.is_running or self.answer_locked:
            return

        text = text.strip()
        if not text:
            return
        try:
            value = int(text)
        except ValueError:
            return

        if value == self.correct_answer:
            self.answer_locked = True
            self.countdown_timer.stop()

            self.score += 1
            if self.score > self.record:
                self.record = self.score

            self.game_page.set_score(self.score)
            self.game_page.set_record(self.record)
            self.game_page.flash_correct()

            QTimer.singleShot(280, self._advance)
        else:
            self.answer_locked = True
            self.countdown_timer.stop()
            self.game_page.flash_wrong()
            QTimer.singleShot(320, lambda: self._lose_game("wrong"))

    def _advance(self):
        if not self.is_running:
            return
        self._new_question()

    def _lose_game(self, reason):
        if not self.is_running:
            return

        self.is_running = False
        self.answer_locked = True
        self.countdown_timer.stop()
        self.game_page.disable_input()

        if reason == "timeout":
            self.game_page.alert_timeout()

        QTimer.singleShot(500, self._show_result)

    def _show_result(self):
        self.result_page.set_result(self.score, self.record)
        self.stack.setCurrentWidget(self.result_page)
        self._fade_in(self.result_page)

    # -- page transition --
    def _fade_in(self, page):
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(340)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # برطرف ساختن باگ پنهان شدن دکمه‌ها: پاکسازی effect پس از پایان انیمیشن
        anim.finished.connect(lambda: page.setGraphicsEffect(None))
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    # -- shutdown --
    def closeEvent(self, event):
        self.countdown_timer.stop()
        super().closeEvent(event)


# ---------- Entry point ----------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("تمرین ضرب")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
