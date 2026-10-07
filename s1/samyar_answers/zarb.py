# -*- coding: utf-8 -*-
"""
تمرین ضرب — Multiplication Trainer
Final Production Build — 50 Stages × 3 Levels × 10 Questions
"""

import sys
import random
from enum import Enum, auto

from PySide6.QtCore import (
    Qt, QTimer, QElapsedTimer, QPropertyAnimation, QVariantAnimation,
    QEasingCurve, QRectF, Signal, QAbstractAnimation, QObject, QSettings,
    QRegularExpression, QPointF
)
from PySide6.QtGui import (
    QColor, QFont, QLinearGradient, QPainter, QBrush, QPen,
    QRadialGradient, QRegularExpressionValidator
)
from PySide6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget, QGraphicsOpacityEffect, QGridLayout,
    QScrollArea, QSizePolicy
)

# =====================================================================
# CONSTANTS
# =====================================================================
MAX_STAGES = 50
LEVELS_PER_STAGE = 3
QUESTIONS_PER_LEVEL = 10
QUESTIONS_PER_STAGE = QUESTIONS_PER_LEVEL * LEVELS_PER_STAGE  # 30
MAX_LIVES = 3
LEVEL_TIME_LIMITS = {1: 15.0, 2: 10.0, 3: 5.0}
BOOST_TIME = 35.0
FEEDBACK_MS = 1800
SKIP_FEEDBACK_MS = 800
COINS_PER_CORRECT = 2
TICK_INTERVAL_MS = 50
WARN_THRESHOLD = 3.0

POWER_COSTS = {"boost": 150, "freeze": 250, "skip": 300}

_FA_TRANS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_DIGIT_TRANS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789"
)


def to_fa(n) -> str:
    return str(n).translate(_FA_TRANS)


def normalize_digits(text: str) -> str:
    return text.translate(_DIGIT_TRANS)


def make_font(size: int, bold: bool = False) -> QFont:
    f = QFont()
    f.setFamilies(["Vazirmatn", "Segoe UI", "Tahoma", "Arial", "sans-serif"])
    f.setPointSize(size)
    f.setBold(bold)
    return f


def safe_int(value, default=0, min_v=None, max_v=None) -> int:
    """Defensive int conversion for corrupted QSettings."""
    try:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return default
        v = int(value)
    except (TypeError, ValueError):
        return default
    if min_v is not None:
        v = max(min_v, v)
    if max_v is not None:
        v = min(max_v, v)
    return v


def parse_int_set(value) -> set:
    """Parse a comma-separated list of ints, filtering invalid entries."""
    result = set()
    if value is None:
        return result
    for part in str(value).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            v = int(part)
        except ValueError:
            continue
        if 1 <= v <= MAX_STAGES:
            result.add(v)
    return result


class GameState(Enum):
    IDLE = auto()
    STAGE_SELECTION = auto()
    PLAYING = auto()
    ANSWER_FEEDBACK = auto()
    STAGE_VICTORY = auto()
    DEFEAT = auto()


# =====================================================================
# THEME
# =====================================================================
class ThemeManager(QObject):
    theme_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.is_dark = False

    def set_dark(self, dark: bool):
        dark = bool(dark)
        if self.is_dark == dark:
            return
        self.is_dark = dark
        self.theme_changed.emit(dark)

    def toggle_theme(self):
        self.set_dark(not self.is_dark)

    def get_colors(self, dark=None) -> dict:
        is_d = self.is_dark if dark is None else bool(dark)
        if is_d:
            return {
                "bg_start": QColor("#1A070E"),
                "bg_mid": QColor("#2A0710"),
                "bg_end": QColor("#120307"),
                "blob_1": QColor(142, 27, 58, 45),
                "blob_2": QColor(90, 11, 24, 50),
                "blob_3": QColor(201, 106, 131, 35),
                "glass_bg": "rgba(42, 7, 16, 0.65)",
                "glass_border": "rgba(201, 106, 131, 0.25)",
                "glass_shadow": QColor(0, 0, 0, 140),
                "text_dark": "#FFF0F4",
                "text_muted": "#D29CA9",
                "primary": "#C96A83",
                "primary_rgb": "201, 106, 131",
                "btn_primary_bg": "rgba(142, 27, 58, 0.90)",
                "btn_primary_bg_hover": "rgba(165, 32, 68, 0.98)",
                "btn_primary_text": "#FFFFFF",
                "btn_secondary_bg": "rgba(42, 7, 16, 0.70)",
                "btn_secondary_bg_hover": "rgba(65, 12, 26, 0.85)",
                "btn_secondary_text": "#C96A83",
                "input_bg": "rgba(28, 6, 12, 0.85)",
                "input_bg_focus": "rgba(38, 8, 16, 0.98)",
                "input_border": "rgba(201, 106, 131, 0.35)",
                "input_border_focus": "rgba(201, 106, 131, 0.90)",
                "warn_red": "#FF5252",
                "correct_bg": "rgba(46, 125, 50, 0.90)",
                "correct_border": "rgba(76, 175, 80, 0.95)",
                "wrong_bg": "rgba(198, 40, 40, 0.90)",
                "wrong_border": "rgba(239, 83, 80, 0.95)",
                "math_symbol": QColor(201, 106, 131, 28),
                "card_locked_bg": "rgba(60, 40, 48, 0.55)",
                "card_locked_text": "#8A6670",
                "card_unlocked_bg": "rgba(142, 27, 58, 0.90)",
                "card_unlocked_text": "#FFFFFF",
                "card_completed_bg": "rgba(46, 125, 50, 0.90)",
                "card_completed_text": "#FFFFFF",
                "scroll_bg": "transparent",
                "scroll_handle": "rgba(201, 106, 131, 0.5)",
            }
        else:
            return {
                "bg_start": QColor("#FFF8FA"),
                "bg_mid": QColor("#FCE8ED"),
                "bg_end": QColor("#F8D5DE"),
                "blob_1": QColor(142, 27, 58, 30),
                "blob_2": QColor(122, 16, 37, 25),
                "blob_3": QColor(201, 106, 131, 35),
                "glass_bg": "rgba(255, 255, 255, 0.65)",
                "glass_border": "rgba(255, 255, 255, 0.90)",
                "glass_shadow": QColor(122, 16, 37, 45),
                "text_dark": "#2A0710",
                "text_muted": "#7A3E4D",
                "primary": "#7A1025",
                "primary_rgb": "122, 16, 37",
                "btn_primary_bg": "rgba(122, 16, 37, 0.92)",
                "btn_primary_bg_hover": "rgba(142, 27, 58, 0.98)",
                "btn_primary_text": "#FFFFFF",
                "btn_secondary_bg": "rgba(255, 255, 255, 0.70)",
                "btn_secondary_bg_hover": "rgba(255, 255, 255, 0.92)",
                "btn_secondary_text": "#7A1025",
                "input_bg": "rgba(255, 255, 255, 0.85)",
                "input_bg_focus": "rgba(255, 255, 255, 0.98)",
                "input_border": "rgba(122, 16, 37, 0.30)",
                "input_border_focus": "rgba(122, 16, 37, 0.85)",
                "warn_red": "#D32F2F",
                "correct_bg": "rgba(232, 245, 233, 0.98)",
                "correct_border": "rgba(76, 175, 80, 0.95)",
                "wrong_bg": "rgba(255, 235, 238, 0.98)",
                "wrong_border": "rgba(244, 67, 54, 0.95)",
                "math_symbol": QColor(122, 16, 37, 22),
                "card_locked_bg": "rgba(200, 190, 195, 0.55)",
                "card_locked_text": "#8A808A",
                "card_unlocked_bg": "rgba(122, 16, 37, 0.92)",
                "card_unlocked_text": "#FFFFFF",
                "card_completed_bg": "rgba(56, 142, 60, 0.92)",
                "card_completed_text": "#FFFFFF",
                "scroll_bg": "transparent",
                "scroll_handle": "rgba(122, 16, 37, 0.4)",
            }


THEME = ThemeManager()


# =====================================================================
# DECORATIVE BACKGROUND
# =====================================================================
class GradientBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark = THEME.is_dark
        THEME.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, is_dark):
        self._is_dark = bool(is_dark)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        c = THEME.get_colors(self._is_dark)

        grad = QLinearGradient(0, 0, r.width(), r.height())
        grad.setColorAt(0.0, c["bg_start"])
        grad.setColorAt(0.5, c["bg_mid"])
        grad.setColorAt(1.0, c["bg_end"])
        p.fillRect(r, QBrush(grad))

        p.setPen(Qt.NoPen)
        p.setBrush(c["blob_1"])
        p.drawEllipse(QRectF(-160, -180, 440, 440))
        p.setBrush(c["blob_2"])
        p.drawEllipse(QRectF(r.width() - 320, r.height() - 280, 480, 480))
        p.setBrush(c["blob_3"])
        p.drawEllipse(QRectF(r.width() * 0.50, 40, 320, 320))

        p.setPen(QPen(c["math_symbol"], 1.5))
        p.setFont(make_font(18, True))
        symbols = ["×", "+", "=", "÷", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"]
        for i in range(18):
            x = (i * 97 + 40) % (max(1, r.width()) + 80) - 40
            y = (i * 73 + 60) % (max(1, r.height()) + 60) - 30
            p.drawText(int(x), int(y), symbols[i % len(symbols)])


# =====================================================================
# GLASS UI PRIMITIVES
# =====================================================================
class GlassCard(QFrame):
    def __init__(self, radius=32, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.setObjectName("glassCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(40)
        self.shadow.setOffset(0, 12)
        self.setGraphicsEffect(self.shadow)
        THEME.theme_changed.connect(self.update_style)
        self.update_style(THEME.is_dark)

    def update_style(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        self.setStyleSheet(f"""
            QFrame#glassCard {{
                background-color: {c['glass_bg']};
                border: 1px solid {c['glass_border']};
                border-radius: {self.radius}px;
            }}
        """)
        self.shadow.setColor(c["glass_shadow"])


class GlassButton(QPushButton):
    def __init__(self, text="", primary=True, parent=None):
        super().__init__(text, parent)
        self._primary = primary
        self._hover = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        self.setFont(make_font(12, True))
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(24)
        self.shadow.setOffset(0, 8)
        self.setGraphicsEffect(self.shadow)
        THEME.theme_changed.connect(self._apply_style)
        self._apply_style()

    def _apply_style(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        if self._primary:
            bg = c["btn_primary_bg_hover"] if self._hover else c["btn_primary_bg"]
            color = c["btn_primary_text"]
            shadow_col = QColor(122, 16, 37, 120) if not THEME.is_dark else QColor(0, 0, 0, 160)
        else:
            bg = c["btn_secondary_bg_hover"] if self._hover else c["btn_secondary_bg"]
            color = c["btn_secondary_text"]
            shadow_col = QColor(0, 0, 0, 40)

        border = c["glass_border"]
        disabled_color = c["text_muted"]
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 16px;
                padding: 8px 16px;
            }}
            QPushButton:pressed {{
                padding-top: 10px;
                padding-bottom: 6px;
            }}
            QPushButton:disabled {{
                color: {disabled_color};
                background-color: rgba(90, 70, 80, 0.25);
                border: 1px solid rgba(150, 130, 140, 0.25);
            }}
        """)
        self.shadow.setColor(shadow_col)

    def enterEvent(self, e):
        self._hover = True
        self._apply_style()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self._apply_style()
        super().leaveEvent(e)


class ThemeToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(48, 48)
        THEME.theme_changed.connect(self.update_state)
        self.clicked.connect(THEME.toggle_theme)
        self.update_state(THEME.is_dark)

    def update_state(self, is_dark=None):
        is_d = THEME.is_dark if is_dark is None else bool(is_dark)
        self.setText("☾" if is_d else "☀")
        c = THEME.get_colors(is_d)
        self.setFont(make_font(16, True))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['glass_bg']};
                color: {c['primary']};
                border: 1px solid {c['glass_border']};
                border-radius: 24px;
            }}
            QPushButton:hover {{
                background-color: {c['btn_secondary_bg_hover']};
            }}
        """)


# =====================================================================
# START PAGE
# =====================================================================
class StartPage(QWidget):
    start_clicked = Signal()
    buy_power = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(10)

        self.coins_label = QLabel("🪙 " + to_fa(0))
        self.coins_label.setAlignment(Qt.AlignCenter)
        self.coins_label.setFont(make_font(18, True))
        layout.addWidget(self.coins_label)

        card = GlassCard(radius=32)
        card.setMaximumWidth(520)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 32, 28, 28)
        card_layout.setSpacing(12)

        self.title = QLabel("تمرین ضرب")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(make_font(30, True))
        card_layout.addWidget(self.title)

        self.sub = QLabel("۵۰ مرحله • ۳ سطح • ۳ جان — رکورد خودت را بشکن!")
        self.sub.setAlignment(Qt.AlignCenter)
        self.sub.setFont(make_font(11))
        self.sub.setWordWrap(True)
        card_layout.addWidget(self.sub)

        shop_title = QLabel("فروشگاه قدرت‌ها")
        shop_title.setAlignment(Qt.AlignCenter)
        shop_title.setFont(make_font(13, True))
        card_layout.addWidget(shop_title)

        shop_grid = QGridLayout()
        shop_grid.setSpacing(8)

        self.btn_boost = GlassButton("⏱ +۳۵ ثانیه\n۱۵۰ 🪙", primary=False)
        self.btn_freeze = GlassButton("❄ فریز تایمر\n۲۵۰ 🪙", primary=False)
        self.btn_skip = GlassButton("⏭ اسکیپ\n۳۰۰ 🪙", primary=False)
        for b in (self.btn_boost, self.btn_freeze, self.btn_skip):
            b.setMinimumHeight(60)

        self.btn_boost.clicked.connect(lambda: self.buy_power.emit("boost"))
        self.btn_freeze.clicked.connect(lambda: self.buy_power.emit("freeze"))
        self.btn_skip.clicked.connect(lambda: self.buy_power.emit("skip"))

        shop_grid.addWidget(self.btn_boost, 0, 0)
        shop_grid.addWidget(self.btn_freeze, 0, 1)
        shop_grid.addWidget(self.btn_skip, 0, 2)
        card_layout.addLayout(shop_grid)

        self.inv_label = QLabel("موجودی: ⏱ ۰   ❄ ۰   ⏭ ۰")
        self.inv_label.setAlignment(Qt.AlignCenter)
        self.inv_label.setFont(make_font(12, True))
        card_layout.addWidget(self.inv_label)

        card_layout.addSpacing(6)

        self.info_badge = QFrame()
        self.info_badge.setObjectName("infoBadge")
        ib = QHBoxLayout(self.info_badge)
        ib.setContentsMargins(12, 6, 12, 6)
        self.info_text = QLabel("سطح ۱ → ۱۵ ثانیه  •  سطح ۲ → ۱۰ ثانیه  •  سطح ۳ → ۵ ثانیه")
        self.info_text.setAlignment(Qt.AlignCenter)
        self.info_text.setFont(make_font(10, True))
        self.info_text.setWordWrap(True)
        ib.addWidget(self.info_text)
        card_layout.addWidget(self.info_badge)

        self.btn_start = GlassButton("ورود به انتخاب مرحله")
        self.btn_start.clicked.connect(self.start_clicked.emit)
        card_layout.addWidget(self.btn_start)

        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(card, 3)
        wrap.addStretch(1)
        layout.addStretch(1)
        layout.addLayout(wrap)
        layout.addStretch(1)

        THEME.theme_changed.connect(self.update_colors)
        self.update_colors(THEME.is_dark)

    def update_coins(self, coins: int):
        self.coins_label.setText(f"🪙 {to_fa(coins)}")

    def update_inventory(self, boost: int, freeze: int, skip: int):
        self.inv_label.setText(
            f"موجودی: ⏱ {to_fa(boost)}   ❄ {to_fa(freeze)}   ⏭ {to_fa(skip)}"
        )

    def update_colors(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        self.title.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        self.sub.setStyleSheet(f"color: {c['text_muted']}; background: transparent;")
        self.coins_label.setStyleSheet(f"color: {c['primary']}; background: transparent;")
        self.inv_label.setStyleSheet(f"color: {c['primary']}; background: transparent;")
        self.info_badge.setStyleSheet(f"""
            QFrame#infoBadge {{
                background-color: {c['input_bg']};
                border: 1px solid {c['input_border']};
                border-radius: 14px;
            }}
        """)
        self.info_text.setStyleSheet(f"color: {c['primary']}; background: transparent;")


# =====================================================================
# STAGE SELECTION
# =====================================================================
class StageCard(QFrame):
    clicked = Signal(int)

    def __init__(self, stage_num: int):
        super().__init__()
        self.stage_num = stage_num
        self._state = "locked"
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(96, 88)
        self.setAttribute(Qt.WA_StyledBackground, True)

        v = QVBoxLayout(self)
        v.setContentsMargins(6, 6, 6, 6)
        v.setSpacing(2)

        self.icon = QLabel("🔒")
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setFont(make_font(16, True))
        v.addWidget(self.icon)

        self.num = QLabel(to_fa(stage_num))
        self.num.setAlignment(Qt.AlignCenter)
        self.num.setFont(make_font(18, True))
        v.addWidget(self.num)

        THEME.theme_changed.connect(self._apply_style)
        self._apply_style()

    def set_state(self, state: str):
        self._state = state
        if state == "completed":
            self.icon.setText("✓")
        elif state == "unlocked":
            self.icon.setText("▶")
        else:
            self.icon.setText("🔒")
        self._apply_style()
        self.setCursor(
            Qt.PointingHandCursor if state != "locked" else Qt.ForbiddenCursor
        )

    def _apply_style(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        if self._state == "completed":
            bg = c["card_completed_bg"]
            fg = c["card_completed_text"]
        elif self._state == "unlocked":
            bg = c["card_unlocked_bg"]
            fg = c["card_unlocked_text"]
        else:
            bg = c["card_locked_bg"]
            fg = c["card_locked_text"]

        self.setStyleSheet(f"""
            StageCard {{
                background-color: {bg};
                border: 1px solid {c['glass_border']};
                border-radius: 18px;
            }}
        """)
        self.num.setStyleSheet(f"color: {fg}; background: transparent;")
        self.icon.setStyleSheet(f"color: {fg}; background: transparent;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._state != "locked":
            self.clicked.emit(self.stage_num)
        super().mousePressEvent(event)


class StageSelectionPage(QWidget):
    stage_selected = Signal(int)
    back_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.stage_cards = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        self.title = QLabel("انتخاب مرحله")
        self.title.setFont(make_font(20, True))
        header.addWidget(self.title)
        header.addStretch(1)
        self.back_btn = GlassButton("بازگشت", primary=False)
        self.back_btn.setMaximumWidth(130)
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(self.back_btn)
        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container.setObjectName("stageContainer")
        container.setAttribute(Qt.WA_StyledBackground, True)
        self.grid = QGridLayout(container)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        columns = 4
        for i in range(MAX_STAGES):
            card = StageCard(i + 1)
            card.clicked.connect(self.stage_selected.emit)
            self.stage_cards[i + 1] = card
            row = i // columns
            col = i % columns
            self.grid.addWidget(card, row, col)

        self.scroll.setWidget(container)
        layout.addWidget(self.scroll, 1)

        THEME.theme_changed.connect(self.update_colors)
        self.update_colors(THEME.is_dark)

    def update_stages(self, unlocked: int, completed: set):
        for num, card in self.stage_cards.items():
            if num in completed:
                card.set_state("completed")
            elif num <= unlocked:
                card.set_state("unlocked")
            else:
                card.set_state("locked")

    def update_colors(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        self.title.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollBar:vertical {{
                background: transparent; width: 10px; margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['scroll_handle']};
                border-radius: 5px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        container = self.scroll.widget()
        if container is not None:
            container.setStyleSheet("background: transparent;")


# =====================================================================
# GAME PAGE
# =====================================================================
class GamePage(QWidget):
    answer_submitted = Signal(str)
    use_power = Signal(str)

    def __init__(self):
        super().__init__()
        self.correct_answer = -1
        self._auto_lock = False
        self._suppress = False

        self.flash_timer = QTimer(self)
        self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self._reset_input_style)

        self.focus_timer = QTimer(self)
        self.focus_timer.setSingleShot(True)
        self.focus_timer.timeout.connect(self._do_focus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 4, 14, 10)
        layout.setSpacing(8)

        stats = QHBoxLayout()
        stats.setSpacing(6)

        self.lives_card = self._make_stat_card("جان", "۳")
        self.level_card = self._make_stat_card("سطح", "۱")
        self.score_card = self._make_stat_card("امتیاز", "۰")
        self.coins_card = self._make_stat_card("سکه", "۰")
        self.record_card = self._make_stat_card("رکورد", "۰")

        stats.addWidget(self.lives_card["frame"], 1)
        stats.addWidget(self.level_card["frame"], 1)
        stats.addWidget(self.score_card["frame"], 1)
        stats.addWidget(self.coins_card["frame"], 1)
        stats.addWidget(self.record_card["frame"], 1)
        layout.addLayout(stats)

        self.stage_progress = QLabel("")
        self.stage_progress.setAlignment(Qt.AlignCenter)
        self.stage_progress.setFont(make_font(11, True))
        layout.addWidget(self.stage_progress)

        self.card = GlassCard(radius=32)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 18, 24, 20)
        card_layout.setSpacing(10)

        self.timer_label = QLabel("15.0")
        self.timer_label.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setFamilies(["Consolas", "Courier New", "monospace"])
        f.setPointSize(22)
        f.setBold(True)
        self.timer_label.setFont(f)
        self.timer_label.setMinimumHeight(32)
        card_layout.addWidget(self.timer_label)

        self.frozen_indicator = QLabel("")
        self.frozen_indicator.setAlignment(Qt.AlignCenter)
        self.frozen_indicator.setFont(make_font(12, True))
        self.frozen_indicator.setMinimumHeight(18)
        card_layout.addWidget(self.frozen_indicator)

        self.question_label = QLabel("۲ × ۳")
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(make_font(48, True))
        self.question_label.setMinimumHeight(80)
        card_layout.addWidget(self.question_label)

        self.input = QLineEdit()
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setFont(make_font(24, True))
        self.input.setPlaceholderText("؟")
        rx = QRegularExpression(r"[0-9۰-۹٠-٩]{0,4}")
        self.input.setValidator(QRegularExpressionValidator(rx, self.input))
        self.input.setMinimumHeight(64)
        self.input.textChanged.connect(self._on_text_changed)
        self.input.returnPressed.connect(self._on_return_pressed)
        card_layout.addWidget(self.input)

        self.correct_label = QLabel("")
        self.correct_label.setAlignment(Qt.AlignCenter)
        self.correct_label.setFont(make_font(18, True))
        self.correct_label.setMinimumHeight(30)
        self.correct_label.hide()
        card_layout.addWidget(self.correct_label)

        layout.addWidget(self.card, 1)

        power_row = QHBoxLayout()
        power_row.setSpacing(8)
        self.btn_p_boost = GlassButton("⏱ ۰", primary=False)
        self.btn_p_freeze = GlassButton("❄ ۰", primary=False)
        self.btn_p_skip = GlassButton("⏭ ۰", primary=False)
        for b in (self.btn_p_boost, self.btn_p_freeze, self.btn_p_skip):
            b.setMinimumHeight(42)
        self.btn_p_boost.clicked.connect(lambda: self.use_power.emit("boost"))
        self.btn_p_freeze.clicked.connect(lambda: self.use_power.emit("freeze"))
        self.btn_p_skip.clicked.connect(lambda: self.use_power.emit("skip"))
        power_row.addWidget(self.btn_p_boost)
        power_row.addWidget(self.btn_p_freeze)
        power_row.addWidget(self.btn_p_skip)
        layout.addLayout(power_row)

        self.hint = QLabel("پاسخ را وارد کن — به‌صورت خودکار ثبت می‌شود")
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setFont(make_font(10))
        layout.addWidget(self.hint)

        THEME.theme_changed.connect(self.update_colors)
        self.update_colors(THEME.is_dark)

    def _make_stat_card(self, title, value):
        frame = GlassCard(radius=16)
        v = QVBoxLayout(frame)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(0)
        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(make_font(9))
        val = QLabel(value)
        val.setAlignment(Qt.AlignCenter)
        val.setFont(make_font(14, True))
        v.addWidget(t)
        v.addWidget(val)
        return {"frame": frame, "title": t, "value": val}

    def begin_question(self, a: int, b: int, answer: int):
        self._suppress = True
        self.input.clear()
        self._suppress = False
        self.correct_answer = int(answer)
        self._auto_lock = False
        self.question_label.setText(f"{to_fa(a)} × {to_fa(b)}")
        self.input.setEnabled(True)
        self.hide_correct_answer()
        self.set_frozen(False)
        self.animate_question()
        self.focus_timer.start(60)

    def _do_focus(self):
        try:
            if self.input.isEnabled() and self.isVisible():
                self.input.setFocus(Qt.OtherFocusReason)
        except RuntimeError:
            pass

    def _on_text_changed(self, text):
        if self._suppress:
            return
        if self._auto_lock:
            return
        norm = normalize_digits(text).strip()
        if not norm:
            return
        try:
            val = int(norm)
        except ValueError:
            return
        if val == self.correct_answer and self.correct_answer >= 0:
            self._auto_lock = True
            self.answer_submitted.emit(str(val))

    def _on_return_pressed(self):
        if self._auto_lock:
            return
        norm = normalize_digits(self.input.text()).strip()
        if not norm:
            return
        self._auto_lock = True
        self.answer_submitted.emit(norm)

    def set_lives(self, n: int):
        self.lives_card["value"].setText(to_fa(max(0, int(n))))

    def set_level(self, lvl: int):
        self.level_card["value"].setText(to_fa(lvl))

    def set_score(self, s: int):
        self.score_card["value"].setText(to_fa(s))

    def set_coins(self, c: int):
        self.coins_card["value"].setText(to_fa(c))

    def set_record(self, r: int):
        self.record_card["value"].setText(to_fa(r))

    def set_stage_progress(self, stage: int, q_in_stage: int):
        self.stage_progress.setText(
            f"مرحله {to_fa(stage)}  •  سؤال {to_fa(q_in_stage)} از {to_fa(QUESTIONS_PER_STAGE)}"
        )

    def set_timer(self, value: float, warning: bool = False):
        self.timer_label.setText(f"{max(0.0, value):.1f}")
        c = THEME.get_colors(THEME.is_dark)
        color = c["warn_red"] if warning else c["primary"]
        self.timer_label.setStyleSheet(f"color: {color}; background: transparent;")

    def set_frozen(self, frozen: bool):
        if frozen:
            self.frozen_indicator.setText("❄ تایمر فریز شد")
            c = THEME.get_colors(THEME.is_dark)
            self.frozen_indicator.setStyleSheet(
                f"color: {c['primary']}; background: transparent;"
            )
        else:
            self.frozen_indicator.setText("")

    def disable_input(self):
        self.input.setEnabled(False)

    def enable_input(self):
        self.input.setEnabled(True)

    def set_power_buttons(self, boost: int, freeze: int, skip: int, enabled: bool = True):
        self.btn_p_boost.setText(f"⏱ {to_fa(boost)}")
        self.btn_p_freeze.setText(f"❄ {to_fa(freeze)}")
        self.btn_p_skip.setText(f"⏭ {to_fa(skip)}")
        self.btn_p_boost.setEnabled(enabled and boost > 0)
        self.btn_p_freeze.setEnabled(enabled and freeze > 0)
        self.btn_p_skip.setEnabled(enabled and skip > 0)

    def animate_question(self):
        label = self.question_label
        anim = QVariantAnimation(self)
        anim.setDuration(280)
        anim.setStartValue(36.0)
        anim.setKeyValueAt(0.55, 54.0)
        anim.setEndValue(48.0)
        anim.setEasingCurve(QEasingCurve.OutBack)

        def on_val(v):
            try:
                size = max(12, int(round(float(v))))
                label.setFont(make_font(size, True))
            except (RuntimeError, TypeError, ValueError):
                pass

        anim.valueChanged.connect(on_val)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def flash_correct(self):
        c = THEME.get_colors(THEME.is_dark)
        self._apply_input_style(custom_border=c["correct_border"], custom_bg=c["correct_bg"])
        self.flash_timer.start(300)

    def flash_wrong(self):
        c = THEME.get_colors(THEME.is_dark)
        self._apply_input_style(custom_border=c["wrong_border"], custom_bg=c["wrong_bg"])
        self.flash_timer.start(340)

    def _reset_input_style(self):
        try:
            self._apply_input_style()
        except RuntimeError:
            pass

    def _apply_input_style(self, custom_border=None, custom_bg=None):
        c = THEME.get_colors(THEME.is_dark)
        bg = custom_bg if custom_bg else c["input_bg"]
        border = custom_border if custom_border else c["input_border"]
        focus_bg = custom_bg if custom_bg else c["input_bg_focus"]
        focus_border = custom_border if custom_border else c["input_border_focus"]
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 20px;
                padding: 6px 14px;
                color: {c['text_dark']};
                selection-background-color: rgba({c['primary_rgb']}, 0.35);
            }}
            QLineEdit:focus {{
                border: 2px solid {focus_border};
                background-color: {focus_bg};
            }}
        """)

    def show_correct_answer(self, answer: int, is_correct: bool):
        color = "#2E7D32" if is_correct else "#C62828"
        self.correct_label.setText(f"پاسخ درست: {to_fa(answer)}")
        self.correct_label.setStyleSheet(f"color: {color}; background: transparent;")
        self.correct_label.show()
        effect = QGraphicsOpacityEffect(self.correct_label)
        self.correct_label.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def hide_correct_answer(self):
        self.correct_label.hide()
        self.correct_label.setText("")

    def update_colors(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        self.question_label.setStyleSheet(
            f"color: {c['text_dark']}; background: transparent;"
        )
        self.hint.setStyleSheet(f"color: {c['text_muted']}; background: transparent;")
        self.stage_progress.setStyleSheet(
            f"color: {c['text_muted']}; background: transparent;"
        )
        for card in (self.lives_card, self.level_card, self.score_card,
                     self.coins_card, self.record_card):
            card["title"].setStyleSheet(
                f"color: {c['text_muted']}; background: transparent;"
            )
            card["value"].setStyleSheet(
                f"color: {c['primary']}; background: transparent;"
            )
        self._apply_input_style()


# =====================================================================
# RESULT PAGE
# =====================================================================
class ResultPage(QWidget):
    primary_clicked = Signal()
    secondary_clicked = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.addStretch(1)

        card = GlassCard(radius=36)
        card.setMaximumWidth(480)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 32, 30, 32)
        card_layout.setSpacing(10)

        self.title = QLabel("نتیجه")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(make_font(26, True))
        card_layout.addWidget(self.title)

        self.reason_label = QLabel("")
        self.reason_label.setAlignment(Qt.AlignCenter)
        self.reason_label.setFont(make_font(13, True))
        self.reason_label.setWordWrap(True)
        card_layout.addWidget(self.reason_label)

        card_layout.addSpacing(6)

        self.score_label = QLabel("")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setFont(make_font(16, True))
        card_layout.addWidget(self.score_label)

        self.stats_label = QLabel("")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(make_font(11))
        self.stats_label.setWordWrap(True)
        card_layout.addWidget(self.stats_label)

        self.coins_label = QLabel("")
        self.coins_label.setAlignment(Qt.AlignCenter)
        self.coins_label.setFont(make_font(13, True))
        card_layout.addWidget(self.coins_label)

        self.record_label = QLabel("")
        self.record_label.setAlignment(Qt.AlignCenter)
        self.record_label.setFont(make_font(12))
        card_layout.addWidget(self.record_label)

        card_layout.addSpacing(14)

        self.btn_primary = GlassButton("ادامه")
        self.btn_primary.clicked.connect(self.primary_clicked.emit)
        card_layout.addWidget(self.btn_primary)

        self.btn_secondary = GlassButton("انتخاب مرحله", primary=False)
        self.btn_secondary.clicked.connect(self.secondary_clicked.emit)
        card_layout.addWidget(self.btn_secondary)

        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(card, 3)
        wrap.addStretch(1)
        layout.addLayout(wrap)
        layout.addStretch(1)

        THEME.theme_changed.connect(self.update_colors)
        self.update_colors(THEME.is_dark)

    def configure(self, victory: bool, stage: int,
                  score: int, record: int, coins_earned: int,
                  correct: int, wrong: int, timeouts: int, skipped: int,
                  reason: str, has_next_stage: bool):
        if victory:
            self.title.setText("مرحله کامل شد!")
            self.reason_label.setStyleSheet(
                "color: #2E7D32; background: transparent;"
            )
            if has_next_stage:
                self.reason_label.setText(f"مرحله {to_fa(stage)} با موفقیت تمام شد")
            else:
                self.reason_label.setText("همهٔ ۵۰ مرحله را کامل کردی! 🎉")
        else:
            self.title.setText("شکست")
            c = THEME.get_colors(THEME.is_dark)
            self.reason_label.setStyleSheet(
                f"color: {c['warn_red']}; background: transparent;"
            )
            self.reason_label.setText(reason)

        self.score_label.setText(f"امتیاز: {to_fa(score)}")
        self.stats_label.setText(
            f"✓ درست: {to_fa(correct)}   ✗ غلط: {to_fa(wrong)}   "
            f"⏱ بی‌پاسخ: {to_fa(timeouts)}   ⏭ رد: {to_fa(skipped)}"
        )
        self.coins_label.setText(f"سکه‌های این دور: +{to_fa(coins_earned)} 🪙")
        self.record_label.setText(f"بهترین رکورد: {to_fa(record)}")

        if victory and has_next_stage:
            self.btn_primary.setText("مرحله بعد")
            self.btn_primary.setVisible(True)
        elif victory and not has_next_stage:
            self.btn_primary.setVisible(False)
        else:
            self.btn_primary.setText("تلاش دوباره")
            self.btn_primary.setVisible(True)

    def update_colors(self, is_dark=None):
        c = THEME.get_colors(is_dark)
        self.title.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        self.score_label.setStyleSheet(f"color: {c['primary']}; background: transparent;")
        self.stats_label.setStyleSheet(f"color: {c['text_muted']}; background: transparent;")
        self.coins_label.setStyleSheet(f"color: {c['primary']}; background: transparent;")
        self.record_label.setStyleSheet(f"color: {c['text_muted']}; background: transparent;")


# =====================================================================
# CINEMATIC OVERLAY (victory / defeat)
# =====================================================================
class CinematicOverlay(QWidget):
    animation_finished = Signal()

    def __init__(self, victory: bool):
        super().__init__()
        self.victory = bool(victory)
        self.phase = 0.0
        self._aborted = False

        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addStretch(1)

        self.symbol = QLabel("✓" if self.victory else "✕")
        self.symbol.setAlignment(Qt.AlignCenter)
        sym_font = QFont()
        sym_font.setFamilies(["Arial", "Segoe UI"])
        sym_font.setPointSize(110)
        sym_font.setBold(True)
        self.symbol.setFont(sym_font)
        layout.addWidget(self.symbol)

        self.title = QLabel("پیروز شدی!" if self.victory else "شکست!")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(make_font(38, True))
        layout.addWidget(self.title)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFont(make_font(15, False))
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        layout.addStretch(1)

        self._effects = {}
        for w in (self.symbol, self.title, self.subtitle):
            eff = QGraphicsOpacityEffect(w)
            eff.setOpacity(0.0)
            w.setGraphicsEffect(eff)
            self._effects[w] = eff

        # Colors per state
        if self.victory:
            self.symbol.setStyleSheet("color: #4ADE80; background: transparent;")
            self.title.setStyleSheet("color: #ECFDF5; background: transparent;")
            self.subtitle.setStyleSheet("color: rgba(236, 253, 245, 0.92); background: transparent;")
        else:
            self.symbol.setStyleSheet("color: #F87171; background: transparent;")
            self.title.setStyleSheet("color: #FEF2F2; background: transparent;")
            self.subtitle.setStyleSheet("color: rgba(254, 242, 242, 0.92); background: transparent;")

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(2600)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.valueChanged.connect(self._on_phase)
        self.anim.finished.connect(self._on_anim_finished)

    def set_subtitle(self, text: str):
        self.subtitle.setText(text)

    def start(self):
        self._aborted = False
        self.phase = 0.0
        self._on_phase(0.0)
        self.anim.stop()
        self.anim.start()

    def stop(self):
        self._aborted = True
        try:
            self.anim.stop()
        except RuntimeError:
            pass

    def _on_phase(self, v):
        try:
            self.phase = float(v)
        except (TypeError, ValueError):
            self.phase = 0.0

        if self.phase < 0.15:
            a = self.phase / 0.15
        elif self.phase > 0.85:
            a = max(0.0, (1.0 - self.phase) / 0.15)
        else:
            a = 1.0
        a = max(0.0, min(1.0, a))

        for eff in self._effects.values():
            try:
                eff.setOpacity(a)
            except RuntimeError:
                pass
        self.update()

    def _on_anim_finished(self):
        if self._aborted:
            return
        self.animation_finished.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        if self.phase < 0.15:
            alpha = self.phase / 0.15
        elif self.phase > 0.85:
            alpha = max(0.0, (1.0 - self.phase) / 0.15)
        else:
            alpha = 1.0
        alpha = max(0.0, min(1.0, alpha))

        if self.victory:
            base = QColor(74, 222, 128)
            dark = QColor(6, 40, 20, 220)
        else:
            base = QColor(248, 113, 113)
            dark = QColor(40, 4, 4, 230)

        ov = QColor(dark)
        ov.setAlpha(int(dark.alpha() * alpha))
        p.fillRect(r, ov)

        t = self.phase

        # First moving light
        cx = r.width() * (0.15 + 0.7 * ((t * 1.7) % 1.0))
        cy = r.height() * (0.2 + 0.6 * ((t * 2.3 + 0.3) % 1.0))
        radius = max(1.0, max(r.width(), r.height()) * 0.6)
        grad = QRadialGradient(QPointF(cx, cy), radius)
        c1 = QColor(base)
        c1.setAlpha(int(160 * alpha))
        c2 = QColor(base)
        c2.setAlpha(0)
        grad.setColorAt(0.0, c1)
        grad.setColorAt(1.0, c2)
        p.fillRect(r, QBrush(grad))

        # Second light
        cx2 = r.width() * (0.8 - 0.6 * ((t * 1.3 + 0.5) % 1.0))
        cy2 = r.height() * (0.7 - 0.5 * ((t * 1.9 + 0.2) % 1.0))
        grad2 = QRadialGradient(QPointF(cx2, cy2), radius * 0.8)
        c3 = QColor(base)
        c3.setAlpha(int(100 * alpha))
        grad2.setColorAt(0.0, c3)
        grad2.setColorAt(1.0, c2)
        p.fillRect(r, QBrush(grad2))


# =====================================================================
# MAIN WINDOW
# =====================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تمرین ضرب")
        self.resize(560, 800)
        self.setMinimumSize(480, 700)

        # -------- Settings (load BEFORE creating UI) --------
        self.settings = QSettings("SamyarGames", "MultiplicationTrainer")
        self._load_settings()

        # -------- Persistent state --------
        self.highest_unlocked_stage = self._loaded_unlocked
        self.completed_stages = self._loaded_completed
        self.coins = self._loaded_coins
        self.inv_boost = self._loaded_boost
        self.inv_freeze = self._loaded_freeze
        self.inv_skip = self._loaded_skip
        self.record = self._loaded_record

        # -------- Session / state management --------
        self.session_id = 0
        self.question_id = 0
        self.game_state = GameState.IDLE

        self.current_stage = 1
        self.current_level = 1
        self.question_in_level = 0
        self.question_in_stage = 0

        self.lives = MAX_LIVES
        self.score = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.timeout_count = 0
        self.skipped_count = 0
        self.coins_this_run = 0

        self.current_a = 0
        self.current_b = 0
        self.correct_answer = 0
        self.time_limit = LEVEL_TIME_LIMITS[1]
        self.time_remaining = self.time_limit
        self.timer_frozen = False
        self.answer_locked = False

        self.stage_victory_processed = False
        self.defeat_processed = False
        self._defeat_reason = ""
        self._closing = False

        # -------- Timers --------
        self.tick_elapsed = QElapsedTimer()
        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(TICK_INTERVAL_MS)
        self.tick_timer.timeout.connect(self._on_tick)

        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self._on_feedback_timeout)
        self.feedback_sid = -1
        self.feedback_qid = -1

        # -------- UI --------
        central = GradientBackground()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(14, 10, 14, 14)
        outer.setSpacing(6)

        top_bar = QHBoxLayout()
        top_bar.addStretch(1)
        self.theme_toggle = ThemeToggleButton()
        top_bar.addWidget(self.theme_toggle)
        outer.addLayout(top_bar)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)

        self.start_page = StartPage()
        self.stage_page = StageSelectionPage()
        self.game_page = GamePage()
        self.result_page = ResultPage()
        self.victory_overlay = CinematicOverlay(victory=True)
        self.defeat_overlay = CinematicOverlay(victory=False)

        self.stack.addWidget(self.start_page)       # 0
        self.stack.addWidget(self.stage_page)       # 1
        self.stack.addWidget(self.game_page)        # 2
        self.stack.addWidget(self.result_page)      # 3
        self.stack.addWidget(self.victory_overlay)  # 4
        self.stack.addWidget(self.defeat_overlay)   # 5

        # -------- Signals --------
        self.start_page.start_clicked.connect(self._go_to_stage_selection)
        self.start_page.buy_power.connect(self._buy_power)
        self.stage_page.stage_selected.connect(self._on_stage_selected)
        self.stage_page.back_clicked.connect(self._go_to_start)
        self.game_page.answer_submitted.connect(self._submit_answer)
        self.game_page.use_power.connect(self._use_power)
        self.result_page.primary_clicked.connect(self._on_result_primary)
        self.result_page.secondary_clicked.connect(self._go_to_stage_selection)
        self.victory_overlay.animation_finished.connect(self._on_victory_overlay_done)
        self.defeat_overlay.animation_finished.connect(self._on_defeat_overlay_done)

        # -------- Initial view --------
        self._refresh_start_ui()
        self.stage_page.update_stages(self.highest_unlocked_stage, self.completed_stages)
        self.game_state = GameState.IDLE
        self.stack.setCurrentWidget(self.start_page)

    # -----------------------------------------------------------------
    # SETTINGS
    # -----------------------------------------------------------------
    def _load_settings(self):
        self._loaded_unlocked = safe_int(
            self.settings.value("highest_unlocked_stage", 1), 1, 1, MAX_STAGES
        )
        self._loaded_completed = parse_int_set(
            self.settings.value("completed_stages", "")
        )
        self._loaded_coins = safe_int(self.settings.value("coins", 0), 0, 0)
        self._loaded_boost = safe_int(self.settings.value("inv_boost", 0), 0, 0)
        self._loaded_freeze = safe_int(self.settings.value("inv_freeze", 0), 0, 0)
        self._loaded_skip = safe_int(self.settings.value("inv_skip", 0), 0, 0)
        self._loaded_record = safe_int(self.settings.value("record", 0), 0, 0)

        dark = self.settings.value("theme_dark", False)
        if isinstance(dark, str):
            dark = dark.strip().lower() in ("true", "1", "yes")
        else:
            dark = bool(dark)

        # Theme must be applied BEFORE creating pages.
        THEME.is_dark = dark

    def _save_settings(self):
        try:
            self.settings.setValue("highest_unlocked_stage", int(self.highest_unlocked_stage))
            self.settings.setValue(
                "completed_stages",
                ",".join(str(s) for s in sorted(self.completed_stages))
            )
            self.settings.setValue("coins", int(self.coins))
            self.settings.setValue("inv_boost", int(self.inv_boost))
            self.settings.setValue("inv_freeze", int(self.inv_freeze))
            self.settings.setValue("inv_skip", int(self.inv_skip))
            self.settings.setValue("record", int(self.record))
            self.settings.setValue("theme_dark", bool(THEME.is_dark))
            self.settings.sync()
        except Exception:
            # Never allow settings persistence issues to crash the game.
            pass

    # -----------------------------------------------------------------
    # UI HELPERS
    # -----------------------------------------------------------------
    def _refresh_start_ui(self):
        self.start_page.update_coins(self.coins)
        self.start_page.update_inventory(self.inv_boost, self.inv_freeze, self.inv_skip)

    def _fade_in(self, page: QWidget):
        try:
            prev = getattr(page, "_fade_anim", None)
            if prev is not None:
                try:
                    prev.stop()
                except RuntimeError:
                    pass
            page._fade_anim = None

            effect = QGraphicsOpacityEffect(page)
            page.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", page)
            anim.setDuration(260)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            page._fade_anim = anim

            def cleanup():
                try:
                    if getattr(page, "_fade_anim", None) is anim:
                        page._fade_anim = None
                        page.setGraphicsEffect(None)
                except RuntimeError:
                    pass

            anim.finished.connect(cleanup)
            anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        except RuntimeError:
            pass

    def _go_to_start(self):
        self._stop_all_gameplay()
        self.game_state = GameState.IDLE
        self._refresh_start_ui()
        self.stack.setCurrentWidget(self.start_page)
        self._fade_in(self.start_page)

    def _go_to_stage_selection(self):
        self._stop_all_gameplay()
        self.game_state = GameState.STAGE_SELECTION
        self.stage_page.update_stages(self.highest_unlocked_stage, self.completed_stages)
        self.stack.setCurrentWidget(self.stage_page)
        self._fade_in(self.stage_page)

    def _on_stage_selected(self, stage_num: int):
        if stage_num < 1 or stage_num > MAX_STAGES:
            return
        if stage_num > self.highest_unlocked_stage and stage_num not in self.completed_stages:
            return
        self._start_stage(stage_num)

    # -----------------------------------------------------------------
    # SHOP
    # -----------------------------------------------------------------
    def _buy_power(self, kind: str):
        cost = POWER_COSTS.get(kind)
        if cost is None:
            return
        if self.coins < cost:
            return
        self.coins -= cost
        if kind == "boost":
            self.inv_boost += 1
        elif kind == "freeze":
            self.inv_freeze += 1
        elif kind == "skip":
            self.inv_skip += 1
        self._save_settings()
        self._refresh_start_ui()

    # -----------------------------------------------------------------
    # GAME LIFECYCLE
    # -----------------------------------------------------------------
    def _stop_all_gameplay(self):
        self.tick_timer.stop()
        self.feedback_timer.stop()
        try:
            self.game_page.flash_timer.stop()
        except RuntimeError:
            pass
        try:
            self.game_page.focus_timer.stop()
        except RuntimeError:
            pass

    def _start_stage(self, stage_num: int):
        # Invalidate old session completely
        self.session_id += 1
        self.question_id += 1

        self._stop_all_gameplay()
        self.victory_overlay.stop()
        self.defeat_overlay.stop()

        self.current_stage = stage_num
        self.current_level = 1
        self.question_in_level = 0
        self.question_in_stage = 0

        self.lives = MAX_LIVES
        self.score = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.timeout_count = 0
        self.skipped_count = 0
        self.coins_this_run = 0

        self.answer_locked = False
        self.timer_frozen = False
        self.stage_victory_processed = False
        self.defeat_processed = False
        self._defeat_reason = ""

        self.game_state = GameState.PLAYING

        # UI refresh
        self.game_page.set_lives(self.lives)
        self.game_page.set_level(self.current_level)
        self.game_page.set_score(self.score)
        self.game_page.set_coins(self.coins)
        self.game_page.set_record(self.record)
        self.game_page.set_power_buttons(
            self.inv_boost, self.inv_freeze, self.inv_skip, enabled=True
        )
        self.game_page.hide_correct_answer()
        self.game_page.enable_input()

        self.stack.setCurrentWidget(self.game_page)
        self._fade_in(self.game_page)

        # First question
        self._start_next_question()

    def _start_next_question(self):
        if self.game_state != GameState.PLAYING:
            return

        self.question_id += 1
        self.question_in_level += 1
        self.question_in_stage += 1

        if self.question_in_stage > QUESTIONS_PER_STAGE:
            # Defensive: should never happen, but protect the state
            self._trigger_victory()
            return

        self.current_a = random.randint(2, 9)
        self.current_b = random.randint(2, 9)
        self.correct_answer = self.current_a * self.current_b
        self.time_limit = LEVEL_TIME_LIMITS.get(self.current_level, 15.0)
        self.time_remaining = self.time_limit
        self.timer_frozen = False
        self.answer_locked = False

        self.game_page.begin_question(
            self.current_a, self.current_b, self.correct_answer
        )
        self.game_page.set_timer(self.time_remaining, warning=False)
        self.game_page.set_level(self.current_level)
        self.game_page.set_stage_progress(self.current_stage, self.question_in_stage)
        self.game_page.set_power_buttons(
            self.inv_boost, self.inv_freeze, self.inv_skip, enabled=True
        )

        self.tick_elapsed.start()
        self.tick_timer.start(TICK_INTERVAL_MS)

    def _on_tick(self):
        if self.game_state != GameState.PLAYING:
            return
        if self.answer_locked:
            return
        if not self.tick_elapsed.isValid():
            return

        delta_ms = self.tick_elapsed.restart()
        if delta_ms < 0:
            delta_ms = TICK_INTERVAL_MS

        if self.timer_frozen:
            return

        self.time_remaining -= delta_ms / 1000.0

        if self.time_remaining <= 0.0:
            self.time_remaining = 0.0
            self.game_page.set_timer(0.0, warning=True)
            self._handle_timeout()
        else:
            self.game_page.set_timer(
                self.time_remaining, warning=(self.time_remaining <= WARN_THRESHOLD)
            )

    # -----------------------------------------------------------------
    # ANSWER SUBMISSION / TIME-OUT / SKIP
    # -----------------------------------------------------------------
    def _submit_answer(self, text: str):
        if self.game_state != GameState.PLAYING:
            return
        if self.answer_locked:
            return

        text = (text or "").strip()
        if not text:
            return
        try:
            value = int(normalize_digits(text))
        except ValueError:
            return

        # Lock FIRST, before any scoring.
        self.answer_locked = True
        self.tick_timer.stop()

        is_correct = (value == self.correct_answer)
        self._apply_result("correct" if is_correct else "wrong")

    def _handle_timeout(self):
        if self.game_state != GameState.PLAYING:
            return
        if self.answer_locked:
            return

        self.answer_locked = True
        self.tick_timer.stop()
        self._apply_result("timeout")

    def _use_power(self, kind: str):
        if self.game_state != GameState.PLAYING:
            return
        if self.answer_locked:
            return

        if kind == "boost":
            if self.inv_boost <= 0:
                return
            self.inv_boost -= 1
            self.time_limit = BOOST_TIME
            self.time_remaining = BOOST_TIME
            self.tick_elapsed.restart()
            self.game_page.set_timer(BOOST_TIME, warning=False)
            self.game_page.set_power_buttons(
                self.inv_boost, self.inv_freeze, self.inv_skip, enabled=True
            )
            self._save_settings()

        elif kind == "freeze":
            if self.inv_freeze <= 0:
                return
            self.inv_freeze -= 1
            self.timer_frozen = True
            self.game_page.set_frozen(True)
            self.game_page.set_power_buttons(
                self.inv_boost, self.inv_freeze, self.inv_skip, enabled=True
            )
            self._save_settings()

        elif kind == "skip":
            if self.inv_skip <= 0:
                return
            self.inv_skip -= 1
            self.game_page.set_power_buttons(
                self.inv_boost, self.inv_freeze, self.inv_skip, enabled=True
            )
            # Lock the question and end it cleanly
            self.answer_locked = True
            self.tick_timer.stop()
            self._save_settings()
            self._apply_result("skip")

    # -----------------------------------------------------------------
    # RESULT APPLICATION
    # -----------------------------------------------------------------
    def _apply_result(self, kind: str):
        # kind in {"correct", "wrong", "timeout", "skip"}
        self.game_state = GameState.ANSWER_FEEDBACK
        self.game_page.disable_input()
        self.game_page.set_power_buttons(
            self.inv_boost, self.inv_freeze, self.inv_skip, enabled=False
        )

        if kind == "correct":
            self.score += 1
            self.correct_count += 1
            self.coins += COINS_PER_CORRECT
            self.coins_this_run += COINS_PER_CORRECT
            if self.score > self.record:
                self.record = self.score
            self.game_page.flash_correct()
        elif kind == "wrong":
            self.lives = max(0, self.lives - 1)
            self.wrong_count += 1
            self.game_page.flash_wrong()
        elif kind == "timeout":
            self.lives = max(0, self.lives - 1)
            self.timeout_count += 1
            self.game_page.flash_wrong()
        elif kind == "skip":
            self.skipped_count += 1
        else:
            return

        self.game_page.set_lives(self.lives)
        self.game_page.set_score(self.score)
        self.game_page.set_coins(self.coins)
        self.game_page.set_record(self.record)

        if kind != "skip":
            self.game_page.show_correct_answer(self.correct_answer, kind == "correct")

        self._save_settings()

        self.feedback_sid = self.session_id
        self.feedback_qid = self.question_id
        delay = SKIP_FEEDBACK_MS if kind == "skip" else FEEDBACK_MS
        self.feedback_timer.start(delay)

    def _on_feedback_timeout(self):
        if self._closing:
            return
        if self.feedback_sid != self.session_id:
            return
        if self.feedback_qid != self.question_id:
            return
        if self.game_state != GameState.ANSWER_FEEDBACK:
            return

        self.game_page.hide_correct_answer()

        # Defeat has priority
        if self.lives <= 0:
            self._trigger_defeat("جان‌هایت تمام شد!")
            return

        # Stage victory
        if self.question_in_stage >= QUESTIONS_PER_STAGE:
            self._trigger_victory()
            return

        # Level up transition
        if self.question_in_level >= QUESTIONS_PER_LEVEL:
            self.current_level = min(LEVELS_PER_STAGE, self.current_level + 1)
            self.question_in_level = 0
            self.game_page.set_level(self.current_level)

        # Continue
        self.game_state = GameState.PLAYING
        self._start_next_question()

    # -----------------------------------------------------------------
    # VICTORY / DEFEAT
    # -----------------------------------------------------------------
    def _trigger_victory(self):
        if self.stage_victory_processed:
            return
        self.stage_victory_processed = True

        self.game_state = GameState.STAGE_VICTORY
        self.tick_timer.stop()
        self.feedback_timer.stop()
        self.game_page.disable_input()
        self.game_page.set_power_buttons(
            self.inv_boost, self.inv_freeze, self.inv_skip, enabled=False
        )

        # Persist progress
        if self.current_stage >= self.highest_unlocked_stage:
            self.highest_unlocked_stage = min(MAX_STAGES, self.current_stage + 1)
        self.completed_stages.add(self.current_stage)

        best_key = f"best_stage_{self.current_stage}"
        old_best = safe_int(self.settings.value(best_key, 0), 0, 0)
        if self.score > old_best:
            try:
                self.settings.setValue(best_key, int(self.score))
            except Exception:
                pass

        self._save_settings()

        if self.current_stage >= MAX_STAGES:
            self.victory_overlay.set_subtitle("همهٔ ۵۰ مرحله را فتح کردی! 🎉")
        else:
            self.victory_overlay.set_subtitle(
                f"مرحله {to_fa(self.current_stage)} با موفقیت کامل شد"
            )

        self.stack.setCurrentWidget(self.victory_overlay)
        self.victory_overlay.start()

    def _trigger_defeat(self, reason: str):
        if self.defeat_processed:
            return
        self.defeat_processed = True

        self.game_state = GameState.DEFEAT
        self.tick_timer.stop()
        self.feedback_timer.stop()
        self.game_page.disable_input()
        self.game_page.set_power_buttons(
            self.inv_boost, self.inv_freeze, self.inv_skip, enabled=False
        )

        self._defeat_reason = reason

        if self.score > self.record:
            self.record = self.score

        self._save_settings()

        self.defeat_overlay.set_subtitle(reason)
        self.stack.setCurrentWidget(self.defeat_overlay)
        self.defeat_overlay.start()

    def _on_victory_overlay_done(self):
        if self.game_state != GameState.STAGE_VICTORY:
            return
        has_next = self.current_stage < MAX_STAGES
        self.result_page.configure(
            victory=True,
            stage=self.current_stage,
            score=self.score,
            record=self.record,
            coins_earned=self.coins_this_run,
            correct=self.correct_count,
            wrong=self.wrong_count,
            timeouts=self.timeout_count,
            skipped=self.skipped_count,
            reason="",
            has_next_stage=has_next,
        )
        self.stack.setCurrentWidget(self.result_page)
        self._fade_in(self.result_page)

    def _on_defeat_overlay_done(self):
        if self.game_state != GameState.DEFEAT:
            return
        self.result_page.configure(
            victory=False,
            stage=self.current_stage,
            score=self.score,
            record=self.record,
            coins_earned=self.coins_this_run,
            correct=self.correct_count,
            wrong=self.wrong_count,
            timeouts=self.timeout_count,
            skipped=self.skipped_count,
            reason=self._defeat_reason,
            has_next_stage=False,
        )
        self.stack.setCurrentWidget(self.result_page)
        self._fade_in(self.result_page)

    def _on_result_primary(self):
        if self.game_state == GameState.STAGE_VICTORY:
            next_stage = min(MAX_STAGES, self.current_stage + 1)
            if self.current_stage < MAX_STAGES and next_stage <= self.highest_unlocked_stage:
                self._start_stage(next_stage)
                return
        elif self.game_state == GameState.DEFEAT:
            # Retry the same stage
            self._start_stage(self.current_stage)
            return
        # Fallback
        self._go_to_stage_selection()

    # -----------------------------------------------------------------
    # CLOSE
    # -----------------------------------------------------------------
    def closeEvent(self, event):
        self._closing = True
        try:
            self._stop_all_gameplay()
            self.victory_overlay.stop()
            self.defeat_overlay.stop()
        except RuntimeError:
            pass
        self._save_settings()
        try:
            super().closeEvent(event)
        except RuntimeError:
            pass


# =====================================================================
# ENTRY POINT
# =====================================================================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("تمرین ضرب")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()