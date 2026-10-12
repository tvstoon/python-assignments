import sys
import os
import math
import random
import time
import wave
import struct
import tempfile
import atexit
from typing import List, Tuple, Dict, Optional

from PySide6.QtCore import (
    Qt, QTimer, QRectF, QPointF, QLineF, QUrl, QSettings, Signal
)
from PySide6.QtGui import (
    QFont, QPen, QBrush, QLinearGradient, QRadialGradient, QImage,
    QPainterPath, QPolygonF, QPainter, QColor, QKeySequence, QShortcut,
    QFontDatabase, QPixmap
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QFrame
)

try:
    from PySide6.QtMultimedia import QSoundEffect
    AUDIO_AVAILABLE = True
except Exception:
    QSoundEffect = None
    AUDIO_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FRUITS = [
    "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐",
    "🍈", "🍒", "🍑", "🍍", "🥥", "🥝", "🍅", "🥭", "🍏"
]

GRAVITY = 250.0
SESSION_SECONDS = 60.0
QUESTION_SECONDS = 5.0
STARTING_LIVES = 3
RUSH_DURATION = 8.0
RUSH_ENERGY_MAX = 100.0
SLICE_RADIUS = 44.0
BOMB_CHANCE = 0.22
MAX_PARTICLES = 260
TRAIL_MAX = 16
TRAIL_LIFETIME = 0.22
MIN_SLICE_SEGMENT = 4.0
PHYSICS_DT_CLAMP = 0.1
MIN_W = 480.0
MIN_H = 360.0

TEMP_FILES: List[str] = []
TEMP_DIRS: List[str] = []

def cleanup_temp_files() -> None:
    for path in list(TEMP_FILES):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
    TEMP_FILES.clear()
    for d in list(TEMP_DIRS):
        try:
            if os.path.isdir(d):
                os.rmdir(d)
        except OSError:
            pass
    TEMP_DIRS.clear()

atexit.register(cleanup_temp_files)

# ---------------------------------------------------------------------------
# Procedural WAV generation
# ---------------------------------------------------------------------------

def generate_wav(filename: str, freq: float, duration: float, kind: str = "sine") -> bool:
    sample_rate = 22050
    n = int(sample_rate * duration)
    if n <= 0:
        return False
    data = bytearray()
    inv_dur = 1.0 / duration if duration > 0.0 else 0.0
    for i in range(n):
        t = i / sample_rate
        val = 0.0
        if kind == "sine":
            val = math.sin(2.0 * math.pi * freq * t)
        elif kind == "slice":
            noise = random.uniform(-1.0, 1.0)
            env = math.exp(-t * 34.0)
            val = noise * env
        elif kind == "bomb":
            noise = random.uniform(-1.0, 1.0)
            f = max(20.0, freq * max(0.15, 1.0 - t * inv_dur))
            sine = math.sin(2.0 * math.pi * f * t)
            env = math.exp(-t * 6.0)
            val = (0.7 * noise + 0.3 * sine) * env
        elif kind == "correct":
            env = math.exp(-t * 8.0)
            val = math.sin(2.0 * math.pi * freq * t) * env
        elif kind == "wrong":
            f = freq * (1.0 - 0.5 * (t * inv_dur))
            env = math.exp(-t * 5.0)
            val = (1.0 if math.sin(2.0 * math.pi * f * t) > 0 else -1.0) * env * 0.5
        elif kind == "combo":
            f = freq * (1.0 + 1.5 * (t * inv_dur))
            env = math.exp(-t * 4.0)
            val = math.sin(2.0 * math.pi * f * t) * env
        else:
            val = math.sin(2.0 * math.pi * freq * t)
        s = int(max(-32768, min(32767, val * 28000)))
        data.extend(struct.pack('<h', s))
    try:
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(bytes(data))
    except (OSError, wave.Error):
        return False
    return True

# ---------------------------------------------------------------------------
# Audio Manager
# ---------------------------------------------------------------------------

class AudioManager:
    def __init__(self) -> None:
        self.muted = False
        self.volume = 0.8
        self.effects: Dict[str, "QSoundEffect"] = {}
        self.temp_dir: Optional[str] = None
        self.enabled = AUDIO_AVAILABLE
        if self.enabled:
            try:
                self.temp_dir = tempfile.mkdtemp(prefix="fruitslash_")
                TEMP_DIRS.append(self.temp_dir)
                self._build_sounds()
            except Exception:
                self.enabled = False
                self.effects = {}

    def _build_sounds(self) -> None:
        if not self.temp_dir:
            return
        specs = {
            "slice": (440.0, 0.08, "slice"),
            "wrong": (150.0, 0.30, "wrong"),
            "bomb": (80.0, 0.50, "bomb"),
            "combo": (587.33, 0.40, "combo"),
            "result": (523.25, 0.55, "correct"),
            "button": (640.0, 0.05, "sine"),
        }
        for name, (f, d, k) in specs.items():
            path = os.path.join(self.temp_dir, f"{name}.wav")
            if not generate_wav(path, f, d, k):
                continue
            try:
                if os.path.getsize(path) <= 44:
                    continue
            except OSError:
                continue
            TEMP_FILES.append(path)
            self._add_effect(name, path)
        for i in range(12):
            f = 440.0 * (1.08 ** i)
            path = os.path.join(self.temp_dir, f"correct_{i}.wav")
            if not generate_wav(path, f, 0.22, "correct"):
                continue
            try:
                if os.path.getsize(path) <= 44:
                    continue
            except OSError:
                continue
            TEMP_FILES.append(path)
            self._add_effect(f"correct_{i}", path)

    def _add_effect(self, name: str, path: str) -> None:
        try:
            e = QSoundEffect()
            e.setSource(QUrl.fromLocalFile(path))
            e.setVolume(0.0 if self.muted else self.volume)
            self.effects[name] = e
        except Exception:
            pass

    def set_muted(self, muted: bool) -> None:
        self.muted = bool(muted)
        self._update_volumes()

    def set_volume(self, volume: float) -> None:
        try:
            v = float(volume)
        except (TypeError, ValueError):
            return
        self.volume = max(0.0, min(1.0, v))
        self._update_volumes()

    def _update_volumes(self) -> None:
        v = 0.0 if self.muted else self.volume
        for e in self.effects.values():
            try:
                e.setVolume(v)
            except Exception:
                pass

    def play(self, name: str) -> None:
        if self.muted or self.volume <= 0.0:
            return
        e = self.effects.get(name)
        if e is None:
            return
        try:
            e.stop()
            e.play()
        except Exception:
            pass

    def play_correct(self, combo_step: int) -> None:
        step = max(0, min(11, int(combo_step)))
        self.play(f"correct_{step}")

    def shutdown(self) -> None:
        for e in list(self.effects.values()):
            try:
                e.stop()
            except Exception:
                pass
        self.effects.clear()
        cleanup_temp_files()

# ---------------------------------------------------------------------------
# Emoji image cache
# ---------------------------------------------------------------------------

class ImageCache:
    def __init__(self) -> None:
        self._cache: Dict[Tuple[str, int], QImage] = {}
        self._font_family: Optional[str] = None

    def _resolve_font(self) -> str:
        if self._font_family is not None:
            return self._font_family
        candidates = [
            "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji",
            "Noto Emoji", "Twemoji", "Symbola", "EmojiOne Color",
        ]
        fam = ""
        try:
            families = set(QFontDatabase.families())
            for c in candidates:
                if c in families:
                    fam = c
                    break
        except Exception:
            fam = ""
        self._font_family = fam
        return fam

    def get_emoji(self, emoji: str, size: int) -> QImage:
        key = (emoji, size)
        img = self._cache.get(key)
        if img is not None:
            return img
        img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            fam = self._resolve_font()
            f = QFont(fam) if fam else QFont()
            f.setPixelSize(max(8, int(size * 0.82)))
            p.setFont(f)
            p.drawText(QRectF(0, 0, size, size),
                       Qt.AlignmentFlag.AlignCenter, emoji)
        finally:
            p.end()
        if len(self._cache) > 240:
            self._cache.clear()
        self._cache[key] = img
        return img

IMAGE_CACHE = ImageCache()

# ---------------------------------------------------------------------------
# Adaptive multiplication learner
# ---------------------------------------------------------------------------

class AdaptiveLearner:
    def __init__(self) -> None:
        self.weights: Dict[Tuple[int, int], float] = {}
        for i in range(1, 13):
            for j in range(1, 13):
                self.weights[(i, j)] = 1.0
        self.last: Optional[Tuple[int, int]] = None

    def next_question(self) -> Tuple[int, int, int]:
        pairs = list(self.weights.keys())
        if not pairs:
            a = random.randint(1, 12)
            b = random.randint(1, 12)
            return a, b, a * b
        weights = [max(0.01, self.weights[p]) for p in pairs]
        if self.last is not None and self.last in self.weights:
            weights[pairs.index(self.last)] *= 0.12
        total = sum(weights)
        if total <= 0.0:
            chosen = random.choice(pairs)
        else:
            r = random.uniform(0.0, total)
            cum = 0.0
            chosen = pairs[-1]
            for p, w in zip(pairs, weights):
                cum += w
                if r <= cum:
                    chosen = p
                    break
        self.last = chosen
        return chosen[0], chosen[1], chosen[0] * chosen[1]

    def record(self, a: int, b: int, correct: bool) -> None:
        for pair in ((a, b), (b, a)):
            if pair not in self.weights:
                continue
            if correct:
                self.weights[pair] = max(0.15, self.weights[pair] * 0.85)
            else:
                self.weights[pair] = min(12.0, self.weights[pair] * 1.55 + 0.4)

# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "decay", "size", "color", "gravity")

    def __init__(self, x: float, y: float, color: QColor, spark: bool = False) -> None:
        angle = random.uniform(0.0, 2.0 * math.pi)
        speed = random.uniform(120.0, 420.0) if spark else random.uniform(60.0, 220.0)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(2.0, 4.0)
        self.size = random.uniform(3.0, 6.0) if spark else random.uniform(4.0, 9.0)
        self.color = QColor(color)
        self.gravity = 320.0

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= self.decay * dt
        return self.life > 0.0

    def draw(self, painter: QPainter) -> None:
        if self.life <= 0.0:
            return
        c = QColor(self.color)
        c.setAlphaF(max(0.0, min(1.0, self.life)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(c))
        s = max(0.5, self.size * self.life)
        painter.drawEllipse(QPointF(self.x, self.y), s, s)

# ---------------------------------------------------------------------------
# Fruit
# ---------------------------------------------------------------------------

class Fruit:
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 emoji: str, answer: int, correct: bool,
                 qid: int, bounds: Tuple[float, float],
                 bomb: bool = False) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.emoji = emoji
        self.answer = int(answer)
        self.correct = bool(correct)
        self.bomb = bool(bomb)
        self.qid = qid
        self.bounds_w, self.bounds_h = bounds
        self.radius = SLICE_RADIUS
        self.rotation = random.uniform(0.0, 360.0)
        self.v_rot = random.uniform(-150.0, 150.0)
        self.sliced = False
        self.slice_angle = 0.0
        self.slice_progress = 0.0
        self.slice_duration = 0.42
        self.active = True
        self.missed = False

    def update(self, dt: float, gravity: float = GRAVITY) -> bool:
        if not self.active:
            return False
        if self.sliced:
            self.slice_progress += dt / self.slice_duration
            if self.slice_progress >= 1.0:
                self.slice_progress = 1.0
                self.active = False
                return False
            return True
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gravity * dt
        self.rotation += self.v_rot * dt
        if (self.y > self.bounds_h + 220.0 or
                self.x < -260.0 or self.x > self.bounds_w + 260.0):
            self.active = False
            return False
        return True

    def check_slice(self, line: QLineF) -> bool:
        if self.sliced or not self.active:
            return False
        p1 = line.p1()
        p2 = line.p2()
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        L2 = dx * dx + dy * dy
        if L2 <= 0.0001:
            d2 = (self.x - p1.x()) ** 2 + (self.y - p1.y()) ** 2
        else:
            t = ((self.x - p1.x()) * dx + (self.y - p1.y()) * dy) / L2
            t = max(0.0, min(1.0, t))
            nx = p1.x() + t * dx
            ny = p1.y() + t * dy
            d2 = (self.x - nx) ** 2 + (self.y - ny) ** 2
        if d2 <= self.radius * self.radius:
            self.sliced = True
            self.slice_angle = math.atan2(dy, dx)
            return True
        return False

    def draw(self, painter: QPainter) -> None:
        if not self.active:
            return
        r = self.radius
        size = int(r * 2.0)
        if not self.sliced:
            painter.save()
            painter.translate(self.x, self.y)
            painter.rotate(self.rotation)
            if self.bomb:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(255, 60, 60, 80)))
                painter.drawEllipse(QPointF(0.0, 0.0), r * 1.18, r * 1.18)
                img = IMAGE_CACHE.get_emoji("💣", size)
                painter.drawImage(QRectF(-r, -r, size, size), img)
            else:
                img = IMAGE_CACHE.get_emoji(self.emoji, size)
                painter.drawImage(QRectF(-r, -r, size, size), img)
            painter.restore()
            if not self.bomb:
                bw, bh = 62.0, 26.0
                badge = QRectF(self.x - bw * 0.5, self.y + r - 6.0, bw, bh)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(16, 21, 34, 232)))
                painter.drawRoundedRect(badge, 13.0, 13.0)
                painter.setPen(QPen(QColor("#F4F7FF")))
                f = QFont()
                f.setPixelSize(14)
                f.setBold(True)
                painter.setFont(f)
                painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, str(self.answer))
        else:
            p = min(1.0, self.slice_progress)
            ease = 1.0 - (1.0 - p) ** 3
            sep = ease * r * 1.15
            fade = max(0.0, 1.0 - p * p)
            sa = self.slice_angle
            dxs = math.cos(sa)
            dys = math.sin(sa)
            img = IMAGE_CACHE.get_emoji("💣" if self.bomb else self.emoji, size)
            W = r * 2.2
            L = r * 2.2
            for side in (-1, 1):
                px = -dys * side
                py = dxs * side
                ox = px * sep
                oy = py * sep
                painter.save()
                painter.setOpacity(fade)
                painter.translate(self.x + ox, self.y + oy)
                poly = QPolygonF([
                    QPointF(dxs * W, dys * W),
                    QPointF(dxs * W + px * L, dys * W + py * L),
                    QPointF(-dxs * W + px * L, -dys * W + py * L),
                    QPointF(-dxs * W, -dys * W),
                ])
                path = QPainterPath()
                path.addPolygon(poly)
                path.closeSubpath()
                painter.setClipPath(path)
                painter.rotate(self.rotation + side * ease * 22.0)
                painter.drawImage(QRectF(-r, -r, size, size), img)
                painter.restore()

# ---------------------------------------------------------------------------
# Game Canvas
# ---------------------------------------------------------------------------

class GameCanvas(QWidget):
    session_ended = Signal(int, int, int, int)

    def __init__(self, audio: AudioManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.audio = audio
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(640, 480)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        self.overlay: Optional[QWidget] = None
        self._bg_cache: Optional[QPixmap] = None

        self.state = "MENU"
        self.last_time = time.monotonic()

        self.q_a = 0
        self.q_b = 0
        self.q_ans = 0
        self.q_id = 0

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.lives = STARTING_LIVES
        self.energy = 0.0
        self.rush = False
        self.rush_timer = 0.0

        self.total_q = 0
        self.correct_q = 0
        self.session_time = SESSION_SECONDS
        self.question_time = QUESTION_SECONDS

        self.fruits: List[Fruit] = []
        self.particles: List[Particle] = []
        self.trail: List[Tuple[QPointF, float]] = []

        self.learner = AdaptiveLearner()
        self.question_resolved = True
        self.next_at: Optional[float] = None

        self.slicing = False
        self._pause_time = 0.0

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._tick)

        self._f_big = QFont()
        self._f_big.setPixelSize(26)
        self._f_big.setBold(True)
        self._f_med = QFont()
        self._f_med.setPixelSize(16)
        self._f_med.setBold(True)
        self._f_small = QFont()
        self._f_small.setPixelSize(14)
        self._f_small.setBold(True)
        self._f_q = QFont()
        self._f_q.setPixelSize(28)
        self._f_q.setBold(True)

    # -- lifecycle ----------------------------------------------------------

    def start(self) -> None:
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.lives = STARTING_LIVES
        self.energy = 0.0
        self.rush = False
        self.rush_timer = 0.0
        self.total_q = 0
        self.correct_q = 0
        self.session_time = SESSION_SECONDS
        self.question_time = QUESTION_SECONDS
        self.fruits.clear()
        self.particles.clear()
        self.trail.clear()
        self.question_resolved = True
        self.next_at = None
        self.slicing = False
        self.state = "PLAYING"
        self.last_time = time.monotonic()
        self._new_question()
        if not self.timer.isActive():
            self.timer.start()
        self.update()

    def pause(self) -> None:
        if self.state == "PLAYING":
            self.state = "PAUSED"
            self.timer.stop()
            self._pause_time = time.monotonic()
            self.slicing = False
            self.trail.clear()
            self.update()

    def resume(self) -> None:
        if self.state == "PAUSED":
            now = time.monotonic()
            if self.next_at is not None:
                self.next_at += now - self._pause_time
            self.state = "PLAYING"
            self.last_time = now
            self.slicing = False
            self.trail.clear()
            self.timer.start()
            self.update()

    def stop(self) -> None:
        self.state = "MENU"
        self.timer.stop()
        self.fruits.clear()
        self.particles.clear()
        self.trail.clear()
        self.next_at = None
        self.question_resolved = True
        self.slicing = False
        self.update()

    # -- question flow ------------------------------------------------------

    def _new_question(self) -> None:
        self.q_id += 1
        self.q_a, self.q_b, self.q_ans = self.learner.next_question()
        self.question_time = QUESTION_SECONDS
        self.question_resolved = False
        self.next_at = None
        self.fruits = [f for f in self.fruits if f.sliced]
        self._spawn_fruits()

    def _spawn_fruits(self) -> None:
        w = max(MIN_W, float(self.width()))
        h = max(MIN_H, float(self.height()))

        num_answers = 4 if self.rush else 3
        has_bomb = (not self.rush) and random.random() < BOMB_CHANCE
        total_items = num_answers + (1 if has_bomb else 0)

        answers: List[int] = [self.q_ans]
        candidates = set()
        for da in (-2, -1, 1, 2, 3, -3):
            for db in (-2, -1, 1, 2):
                na = self.q_a + da
                nb = self.q_b + db
                if na < 1 or nb < 1:
                    continue
                v = na * nb
                if v > 0 and v != self.q_ans:
                    candidates.add(v)
        for delta in (-12, -8, -6, -4, 4, 6, 8, 12):
            v = self.q_ans + delta
            if v > 0 and v != self.q_ans:
                candidates.add(v)
        pool = [c for c in candidates if 1 <= c <= 200]
        random.shuffle(pool)
        while len(answers) < num_answers and pool:
            v = pool.pop()
            if v not in answers:
                answers.append(v)
        guard = 0
        while len(answers) < num_answers and guard < 200:
            guard += 1
            v = random.randint(1, 144)
            if v != self.q_ans and v not in answers:
                answers.append(v)
        while len(answers) < num_answers:
            answers.append(self.q_ans + len(answers) + 1)

        random.shuffle(answers)

        emoji_pool = list(FRUITS)
        random.shuffle(emoji_pool)
        while len(emoji_pool) < total_items:
            emoji_pool.extend(FRUITS)

        slot_w = w / float(total_items)
        ans_idx = 0
        for i in range(total_items):
            x = slot_w * (i + 0.5) + random.uniform(-22.0, 22.0)
            x = max(SLICE_RADIUS + 8.0, min(w - SLICE_RADIUS - 8.0, x))
            y = h + 60.0
            vx = (w * 0.5 - x) * random.uniform(0.55, 1.05)
            peak_y = h * 0.22
            delta = max(120.0, (h + 60.0) - peak_y)
            vy = -math.sqrt(2.0 * GRAVITY * delta) * random.uniform(0.94, 1.06)
            if has_bomb and i == total_items - 1:
                fruit = Fruit(x, y, vx, vy, "💣", 0, False,
                              self.q_id, (w, h), bomb=True)
            else:
                ans = answers[ans_idx] if ans_idx < len(answers) else self.q_ans
                ans_idx += 1
                fruit = Fruit(x, y, vx, vy, emoji_pool[i], ans,
                              ans == self.q_ans, self.q_id, (w, h))
            self.fruits.append(fruit)

    def _schedule_next(self, delay: float) -> None:
        self.next_at = time.monotonic() + max(0.05, delay)

    # -- resolution ---------------------------------------------------------

    def _resolve_correct(self) -> None:
        if self.question_resolved:
            return
        self.question_resolved = True
        self.total_q += 1
        self.correct_q += 1
        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        base = 100
        speed_bonus = int(50.0 * max(0.0, self.question_time / QUESTION_SECONDS))
        mult = 1 + (self.combo // 5)
        gained = (base + speed_bonus) * mult
        if self.rush:
            gained *= 2
        self.score += gained

        if not self.rush:
            self.energy = min(RUSH_ENERGY_MAX, self.energy + 14.0)
            if self.energy >= RUSH_ENERGY_MAX:
                self.rush = True
                self.rush_timer = RUSH_DURATION
                self.energy = 0.0
                self.audio.play("combo")
            else:
                self.audio.play_correct(self.combo - 1)
        else:
            self.audio.play_correct(self.combo - 1)

        self.learner.record(self.q_a, self.q_b, True)
        self._schedule_next(0.35)

    def _resolve_wrong(self) -> None:
        if self.question_resolved:
            return
        self.question_resolved = True
        self.total_q += 1
        self.combo = 0
        self.energy = max(0.0, self.energy - 30.0)
        self.lives -= 1
        self.learner.record(self.q_a, self.q_b, False)
        self.audio.play("wrong")
        if self.lives <= 0:
            self._end_session()
            return
        self._schedule_next(0.55)

    def _resolve_bomb(self) -> None:
        if self.question_resolved:
            return
        self.question_resolved = True
        self.total_q += 1
        self.combo = 0
        self.energy = max(0.0, self.energy - 45.0)
        self.lives -= 1
        self.learner.record(self.q_a, self.q_b, False)
        self.audio.play("bomb")
        if self.lives <= 0:
            self._end_session()
            return
        self._schedule_next(0.55)

    def _resolve_missed(self) -> None:
        if self.question_resolved:
            return
        self.question_resolved = True
        self.total_q += 1
        self.combo = 0
        self.energy = max(0.0, self.energy - 15.0)
        self.lives -= 1
        self.learner.record(self.q_a, self.q_b, False)
        self.audio.play("wrong")
        if self.lives <= 0:
            self._end_session()
            return
        self._schedule_next(0.5)

    def _end_session(self) -> None:
        if self.state != "PLAYING":
            return
        self.state = "RESULTS"
        self.timer.stop()
        self.next_at = None
        self.question_resolved = True
        self.fruits.clear()
        self.particles.clear()
        self.trail.clear()
        self.slicing = False
        try:
            self.audio.play("result")
        except Exception:
            pass
        self.session_ended.emit(
            int(self.score), int(self.correct_q), int(self.total_q), int(self.max_combo)
        )
        self.update()

    # -- game loop ----------------------------------------------------------

    def _tick(self) -> None:
        now = time.monotonic()
        real_dt = now - self.last_time
        self.last_time = now
        if real_dt < 0.0:
            real_dt = 0.0
        physics_dt = real_dt if real_dt < PHYSICS_DT_CLAMP else PHYSICS_DT_CLAMP

        if self.state != "PLAYING":
            return

        self.session_time -= real_dt
        if self.session_time <= 0.0:
            self.session_time = 0.0
            self._end_session()
            return

        if self.rush:
            self.rush_timer -= real_dt
            if self.rush_timer <= 0.0:
                self.rush = False
                self.rush_timer = 0.0

        if self.trail:
            cutoff = now - TRAIL_LIFETIME
            if self.trail[0][1] < cutoff:
                self.trail = [(pt, t) for pt, t in self.trail if t >= cutoff]

        if self.particles:
            keep = []
            for pt in self.particles:
                if pt.update(physics_dt):
                    keep.append(pt)
            self.particles = keep
            if len(self.particles) > MAX_PARTICLES:
                del self.particles[:len(self.particles) - MAX_PARTICLES]

        correct_missed = False
        if self.fruits:
            keep_fruits: List[Fruit] = []
            for f in self.fruits:
                if f.update(physics_dt):
                    keep_fruits.append(f)
                else:
                    if (not f.sliced) and f.correct and (not f.missed) \
                            and f.qid == self.q_id:
                        correct_missed = True
            self.fruits = keep_fruits

        if not self.question_resolved:
            self.question_time -= real_dt
            if self.question_time <= 0.0:
                self.question_time = 0.0
                self._resolve_missed()
                return
            if correct_missed:
                self._resolve_missed()
                return

        if self.next_at is not None and now >= self.next_at:
            self.next_at = None
            self._new_question()

        self.update()

    # -- input --------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if self.state != "PLAYING":
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        try:
            pos = event.position()
        except AttributeError:
            pos = QPointF(event.pos())
        self.slicing = True
        self.trail = [(QPointF(pos), time.monotonic())]

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.slicing = False

    def mouseMoveEvent(self, event) -> None:
        if self.state != "PLAYING" or not self.slicing:
            return
        try:
            pos = event.position()
        except AttributeError:
            pos = QPointF(event.pos())
        now = time.monotonic()
        if self.trail:
            last = self.trail[-1][0]
            line = QLineF(last, pos)
            if line.length() >= MIN_SLICE_SEGMENT:
                self._slice_line(line)
        self.trail.append((QPointF(pos), now))
        if len(self.trail) > TRAIL_MAX:
            del self.trail[:len(self.trail) - TRAIL_MAX]

    def _slice_line(self, line: QLineF) -> None:
        if not self.fruits:
            return
        hits: List[Fruit] = []
        for f in self.fruits:
            if f.sliced or not f.active:
                continue
            if f.check_slice(line):
                hits.append(f)
                self._spawn_slice_particles(f)
        if not hits:
            return
        self.audio.play("slice")
        if self.question_resolved:
            return
        qid_hits = [f for f in hits if f.qid == self.q_id]
        if not qid_hits:
            return
        if any(f.bomb for f in qid_hits):
            self._resolve_bomb()
        elif any(f.correct for f in qid_hits):
            self._resolve_correct()
        else:
            self._resolve_wrong()

    def _spawn_slice_particles(self, fruit: Fruit) -> None:
        if fruit.bomb:
            colors = [QColor("#FF5D73"), QColor("#FFB300")]
            n = 20
        else:
            colors = [QColor("#FFD24A"), QColor("#FF8A3D"), QColor("#36D6B0")]
            n = 14
        for i in range(n):
            c = colors[i % len(colors)]
            self.particles.append(Particle(fruit.x, fruit.y, c, spark=True))

    # -- painting -----------------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._bg_cache = None
        w = float(max(MIN_W, self.width()))
        h = float(max(MIN_H, self.height()))
        for f in self.fruits:
            f.bounds_w = w
            f.bounds_h = h
        if self.overlay is not None:
            self.overlay.setGeometry(0, 0, self.width(), self.height())

    def _ensure_bg(self) -> Optional[QPixmap]:
        if self._bg_cache is not None and \
                self._bg_cache.width() == self.width() and \
                self._bg_cache.height() == self.height():
            return self._bg_cache
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return None
        pm = QPixmap(w, h)
        p = QPainter(pm)
        try:
            grad = QLinearGradient(0.0, 0.0, 0.0, float(h))
            grad.setColorAt(0.0, QColor("#3A2317"))
            grad.setColorAt(0.45, QColor("#2A1810"))
            grad.setColorAt(1.0, QColor("#170C06"))
            p.fillRect(0, 0, w, h, QBrush(grad))

            p.setPen(QPen(QColor(0, 0, 0, 70), 1))
            plank = 76
            y = plank
            while y < h:
                p.drawLine(0, y, w, y)
                y += plank

            p.setPen(QPen(QColor(0, 0, 0, 40), 1))
            y = plank // 2
            while y < h:
                p.drawLine(0, y, w, y)
                y += plank

            rad = QRadialGradient(QPointF(w * 0.5, h * 0.5),
                                  max(w, h) * 0.78)
            rad.setColorAt(0.0, QColor(0, 0, 0, 0))
            rad.setColorAt(0.65, QColor(0, 0, 0, 40))
            rad.setColorAt(1.0, QColor(0, 0, 0, 150))
            p.fillRect(0, 0, w, h, QBrush(rad))
        finally:
            p.end()
        self._bg_cache = pm
        return pm

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

            bg = self._ensure_bg()
            if bg is not None:
                painter.drawPixmap(0, 0, bg)
            else:
                painter.fillRect(self.rect(), QColor("#1A0F08"))

            for f in self.fruits:
                f.draw(painter)
            for pt in self.particles:
                pt.draw(painter)

            if self.state == "PLAYING":
                self._draw_trail(painter)

            if self.state in ("PLAYING", "PAUSED"):
                self._draw_hud(painter)
        finally:
            painter.end()

    def _draw_trail(self, painter: QPainter) -> None:
        if len(self.trail) < 2:
            return
        path = QPainterPath()
        path.moveTo(self.trail[0][0])
        for pt, _ in self.trail[1:]:
            path.lineTo(pt)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QBrush(QColor(54, 214, 176, 190)), 7.0,
                   Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        pen2 = QPen(QBrush(QColor(255, 255, 255, 230)), 2.0,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen2)
        painter.drawPath(path)

    def _draw_hud(self, painter: QPainter) -> None:
        w = self.width()

        # question box
        qw = 300.0
        qh = 66.0
        q_rect = QRectF((w - qw) * 0.5, 14.0, qw, qh)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(12, 16, 28, 224)))
        painter.drawRoundedRect(q_rect, 16.0, 16.0)
        painter.setPen(QPen(QColor(255, 210, 74, 90), 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(q_rect, 16.0, 16.0)
        painter.setPen(QPen(QColor("#F4F7FF")))
        painter.setFont(self._f_q)
        painter.drawText(q_rect, Qt.AlignmentFlag.AlignCenter,
                         f"{self.q_a} × {self.q_b} = ?")

        # question timer bar
        bar_w = 260.0
        bar_x = (w - bar_w) * 0.5
        bar_y = q_rect.bottom() + 8.0
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 36)))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, 7.0), 4.0, 4.0)
        ratio = 0.0
        if not self.question_resolved:
            ratio = max(0.0, min(1.0, self.question_time / QUESTION_SECONDS))
        if ratio > 0.0:
            if ratio < 0.3:
                bar_color = QColor("#FF5D73")
            elif ratio < 0.6:
                bar_color = QColor("#FFD24A")
            else:
                bar_color = QColor("#36D6B0")
            painter.setBrush(QBrush(bar_color))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w * ratio, 7.0),
                                    4.0, 4.0)

        # top-left score & timer
        painter.setFont(self._f_big)
        painter.setPen(QPen(QColor("#FFD24A")))
        painter.drawText(22, 44, f"{self.score}")
        painter.setFont(self._f_small)
        painter.setPen(QPen(QColor("#AAB5CC")))
        painter.drawText(22, 24, "SCORE")

        painter.setFont(self._f_big)
        painter.setPen(QPen(QColor("#36D6B0")))
        painter.drawText(22, 86, f"{int(math.ceil(self.session_time))}s")
        painter.setFont(self._f_small)
        painter.setPen(QPen(QColor("#AAB5CC")))
        painter.drawText(22, 68, "TIME")

        # energy bar
        e_x, e_y, e_w, e_h = 22.0, 100.0, 168.0, 12.0
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 36)))
        painter.drawRoundedRect(QRectF(e_x, e_y, e_w, e_h), 6.0, 6.0)
        if self.rush:
            ef = max(0.0, min(1.0, self.rush_timer / RUSH_DURATION))
            e_col = QColor("#FF8A3D")
        else:
            ef = max(0.0, min(1.0, self.energy / RUSH_ENERGY_MAX))
            e_col = QColor("#237BFF")
        if ef > 0.0:
            painter.setBrush(QBrush(e_col))
            painter.drawRoundedRect(QRectF(e_x, e_y, e_w * ef, e_h), 6.0, 6.0)
        painter.setFont(self._f_small)
        painter.setPen(QPen(QColor("#AAB5CC")))
        label = "RUSH" if self.rush else "ENERGY"
        painter.drawText(int(e_x + e_w + 8), int(e_y + 11), label)

        # top-right lives / combo
        painter.setFont(self._f_small)
        painter.setPen(QPen(QColor("#AAB5CC")))
        painter.drawText(w - 22 - 130, 24, "LIVES")
        hearts = "❤ " * max(0, self.lives)
        painter.setFont(self._f_med)
        painter.setPen(QPen(QColor("#FF5D73")))
        painter.drawText(w - 22 - 130, 48, hearts if hearts else "—")

        if self.combo > 1:
            painter.setFont(self._f_med)
            painter.setPen(QPen(QColor("#FFD24A")))
            painter.drawText(w - 22 - 130, 76, f"COMBO ×{self.combo}")

        if self.rush:
            painter.setFont(self._f_med)
            painter.setPen(QPen(QColor("#FF8A3D")))
            painter.drawText(w - 22 - 130, 100,
                             f"RUSH  {self.rush_timer:0.1f}s  (2×)")

# ---------------------------------------------------------------------------
# Styled widgets
# ---------------------------------------------------------------------------

class StyledButton(QPushButton):
    def __init__(self, text: str, primary: bool = False,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)
        f = QFont()
        f.setPixelSize(16)
        f.setBold(True)
        self.setFont(f)
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF5D73;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 11px;
                    padding: 10px 26px;
                }
                QPushButton:hover { background-color: #FF7A8C; }
                QPushButton:pressed { background-color: #D94860; }
                QPushButton:disabled { background-color: #555; color: #999; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #237BFF;
                    color: #F4F7FF;
                    border: none;
                    border-radius: 11px;
                    padding: 10px 26px;
                }
                QPushButton:hover { background-color: #36D6B0; color: #0B0F1A; }
                QPushButton:pressed { background-color: #1D62CD; color: #F4F7FF; }
                QPushButton:disabled { background-color: #555; color: #999; }
            """)

class MainMenuWidget(QWidget):
    play_requested = Signal()
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("menuRoot")
        self.setStyleSheet("""
            QWidget#menuRoot {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2A1810, stop:0.55 #181226, stop:1 #0B0F1A);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("FRUIT SLASH")
        tf = QFont()
        tf.setPixelSize(56)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color: #FFD24A; letter-spacing: 4px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Multiplication Arcade")
        sf = QFont()
        sf.setPixelSize(18)
        subtitle.setFont(sf)
        subtitle.setStyleSheet("color: #AAB5CC; letter-spacing: 1px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stats_label = QLabel("")
        stf = QFont()
        stf.setPixelSize(15)
        stf.setBold(True)
        self.stats_label.setFont(stf)
        self.stats_label.setStyleSheet("color: #36D6B0;")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hint_label = QLabel("Slice the fruit with the correct answer.  Arrow keys not required — use your mouse.")
        hf = QFont()
        hf.setPixelSize(12)
        self.hint_label.setFont(hf)
        self.hint_label.setStyleSheet("color: #6B7794;")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_play = StyledButton("PLAY", primary=True)
        btn_play.setFixedSize(250, 58)
        btn_play.clicked.connect(self.play_requested.emit)

        btn_settings = StyledButton("SETTINGS")
        btn_settings.setFixedSize(250, 48)
        btn_settings.clicked.connect(self.settings_requested.emit)

        btn_exit = StyledButton("EXIT")
        btn_exit.setFixedSize(250, 48)
        btn_exit.clicked.connect(self.exit_requested.emit)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(14)
        layout.addWidget(self.stats_label)
        layout.addSpacing(28)
        layout.addWidget(btn_play, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_settings, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_exit, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.hint_label)
        layout.addStretch(1)

    def update_stats(self, best: int, xp: int, rank: str) -> None:
        self.stats_label.setText(
            f"BEST  {best}        XP  {xp}        RANK  {rank.upper()}"
        )

class SettingsWidget(QWidget):
    back_requested = Signal()
    volume_changed = Signal(float)
    mute_changed = Signal(bool)

    def __init__(self, audio: AudioManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.audio = audio
        self.setObjectName("settingsRoot")
        self.setStyleSheet("""
            QWidget#settingsRoot {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #181226, stop:1 #0B0F1A);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("SETTINGS")
        tf = QFont()
        tf.setPixelSize(36)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color: #FFD24A; letter-spacing: 3px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mute_cb = QCheckBox("Mute audio")
        self.mute_cb.setStyleSheet("""
            QCheckBox { color: #F4F7FF; font-size: 15px; spacing: 10px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)
        self.mute_cb.setChecked(bool(self.audio.muted))
        self.mute_cb.toggled.connect(self._on_mute)

        vol_row = QHBoxLayout()
        vol_row.setSpacing(14)
        vol_label = QLabel("Volume")
        vol_label.setStyleSheet("color: #F4F7FF; font-size: 15px;")
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(round(self.audio.volume * 100.0)))
        self.vol_slider.setFixedWidth(240)
        self.vol_slider.valueChanged.connect(self._on_volume)
        self.vol_value = QLabel(f"{int(round(self.audio.volume * 100.0))}%")
        self.vol_value.setStyleSheet("color: #AAB5CC; font-size: 14px;")
        self.vol_value.setFixedWidth(50)
        vol_row.addWidget(vol_label)
        vol_row.addWidget(self.vol_slider)
        vol_row.addWidget(self.vol_value)

        btn_back = StyledButton("BACK")
        btn_back.setFixedWidth(220)
        btn_back.clicked.connect(self.back_requested.emit)

        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.mute_cb, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(vol_row)
        layout.addSpacing(24)
        layout.addWidget(btn_back, 0, Qt.AlignmentFlag.AlignCenter)

    def _on_mute(self, checked: bool) -> None:
        self.audio.set_muted(bool(checked))
        self.mute_changed.emit(bool(checked))

    def _on_volume(self, v: int) -> None:
        v = max(0, min(100, int(v)))
        self.audio.set_volume(v / 100.0)
        self.vol_value.setText(f"{v}%")
        self.volume_changed.emit(v / 100.0)

class PauseOverlay(QWidget):
    resume_requested = Signal()
    restart_requested = Signal()
    menu_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(6, 9, 18, 210);")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("pausePanel")
        panel.setFixedSize(320, 340)
        panel.setStyleSheet("""
            QFrame#pausePanel {
                background-color: #171D35;
                border-radius: 18px;
                border: 1px solid #2A3352;
            }
        """)
        pl = QVBoxLayout(panel)
        pl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pl.setSpacing(14)
        pl.setContentsMargins(28, 28, 28, 28)

        t = QLabel("PAUSED")
        tf = QFont()
        tf.setPixelSize(30)
        tf.setBold(True)
        t.setFont(tf)
        t.setStyleSheet("color: #FFD24A; letter-spacing: 2px;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)

        b1 = StyledButton("RESUME", primary=True)
        b1.clicked.connect(self.resume_requested.emit)
        b2 = StyledButton("RESTART")
        b2.clicked.connect(self.restart_requested.emit)
        b3 = StyledButton("MAIN MENU")
        b3.clicked.connect(self.menu_requested.emit)

        pl.addWidget(t, 0, Qt.AlignmentFlag.AlignCenter)
        pl.addSpacing(14)
        pl.addWidget(b1)
        pl.addWidget(b2)
        pl.addWidget(b3)

        outer.addWidget(panel)

    def mousePressEvent(self, event) -> None:
        event.accept()

class ResultsWidget(QWidget):
    play_again_requested = Signal()
    menu_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("resultsRoot")
        self.setStyleSheet("""
            QWidget#resultsRoot {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #241031, stop:1 #0B0F1A);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)

        self.title_label = QLabel("SESSION COMPLETE")
        tf = QFont()
        tf.setPixelSize(34)
        tf.setBold(True)
        self.title_label.setFont(tf)
        self.title_label.setStyleSheet("color: #FFD24A; letter-spacing: 3px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.score_label = QLabel("0")
        sfl = QFont()
        sfl.setPixelSize(76)
        sfl.setBold(True)
        self.score_label.setFont(sfl)
        self.score_label.setStyleSheet("color: #36D6B0;")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.score_caption = QLabel("FINAL SCORE")
        cf = QFont()
        cf.setPixelSize(13)
        cf.setBold(True)
        self.score_caption.setFont(cf)
        self.score_caption.setStyleSheet("color: #6B7794; letter-spacing: 3px;")
        self.score_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stats_label = QLabel("")
        stf = QFont()
        stf.setPixelSize(16)
        self.stats_label.setFont(stf)
        self.stats_label.setStyleSheet("color: #F4F7FF;")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.xp_label = QLabel("")
        xf = QFont()
        xf.setPixelSize(20)
        xf.setBold(True)
        self.xp_label.setFont(xf)
        self.xp_label.setStyleSheet("color: #FF8A3D;")
        self.xp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_again = StyledButton("PLAY AGAIN", primary=True)
        btn_again.setFixedSize(240, 54)
        btn_again.clicked.connect(self.play_again_requested.emit)

        btn_menu = StyledButton("MAIN MENU")
        btn_menu.setFixedSize(240, 48)
        btn_menu.clicked.connect(self.menu_requested.emit)

        layout.addStretch(1)
        layout.addWidget(self.title_label)
        layout.addSpacing(6)
        layout.addWidget(self.score_caption)
        layout.addWidget(self.score_label)
        layout.addSpacing(12)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.xp_label)
        layout.addSpacing(24)
        layout.addWidget(btn_again, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_menu, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

    def set_results(self, score: int, correct: int, total: int,
                    max_combo: int, xp: int) -> None:
        acc = int(round(100.0 * correct / total)) if total > 0 else 0
        self.score_label.setText(str(score))
        self.stats_label.setText(
            f"Correct:  {correct} / {total}        Accuracy:  {acc}%\n"
            f"Max Combo:  ×{max_combo}"
        )
        self.xp_label.setText(f"+{xp} XP earned")

# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fruit Slash — Multiplication Arcade")
        self.resize(980, 700)
        self.setMinimumSize(760, 560)
        self.setStyleSheet("background-color: #0B0F1A;")

        self.settings = QSettings("FruitSlash", "Progression")
        self.best_score = self._safe_int(self.settings.value("best_score", 0), 0)
        self.total_xp = self._safe_int(self.settings.value("total_xp", 0), 0)
        self.volume = self._safe_float(self.settings.value("volume", 0.8), 0.8)
        self.muted = self._safe_bool(self.settings.value("muted", False), False)

        self.audio = AudioManager()
        self.audio.set_volume(self.volume)
        self.audio.set_muted(self.muted)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MainMenuWidget()
        self.canvas = GameCanvas(self.audio)
        self.settings_widget = SettingsWidget(self.audio)
        self.results = ResultsWidget()

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.canvas)
        self.stack.addWidget(self.settings_widget)
        self.stack.addWidget(self.results)

        self.pause_overlay = PauseOverlay(self.canvas)
        self.canvas.overlay = self.pause_overlay
        self.pause_overlay.setGeometry(0, 0, self.canvas.width(), self.canvas.height())
        self.pause_overlay.hide()

        # signals
        self.menu.play_requested.connect(self._start_game)
        self.menu.settings_requested.connect(self._open_settings)
        self.menu.exit_requested.connect(self.close)

        self.settings_widget.back_requested.connect(self._close_settings)
        self.settings_widget.volume_changed.connect(self._on_volume_changed)
        self.settings_widget.mute_changed.connect(self._on_mute_changed)

        self.canvas.session_ended.connect(self._on_session_ended)

        self.pause_overlay.resume_requested.connect(self._resume_game)
        self.pause_overlay.restart_requested.connect(self._start_game)
        self.pause_overlay.menu_requested.connect(self._go_to_menu)

        self.results.play_again_requested.connect(self._start_game)
        self.results.menu_requested.connect(self._go_to_menu)

        # shortcuts
        self._sc_esc = QShortcut(QKeySequence("Escape"), self)
        self._sc_esc.activated.connect(self._on_escape)
        self._sc_p = QShortcut(QKeySequence("P"), self)
        self._sc_p.activated.connect(self._on_escape)

        # button click sounds
        for btn in self.findChildren(QPushButton):
            try:
                btn.clicked.connect(self._play_click)
            except Exception:
                pass

        self._refresh_menu_stats()

    # -- settings helpers ---------------------------------------------------

    @staticmethod
    def _safe_int(v, default: int = 0) -> int:
        try:
            if v is None:
                return default
            return int(v)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_float(v, default: float = 0.0) -> float:
        try:
            if v is None:
                return default
            return float(v)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_bool(v, default: bool = False) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return default
        s = str(v).strip().lower()
        if s in ("true", "1", "yes", "on"):
            return True
        if s in ("false", "0", "no", "off", ""):
            return False
        return default

    def _rank(self) -> str:
        xp = self.total_xp
        if xp >= 5000:
            return "Diamond"
        if xp >= 2500:
            return "Platinum"
        if xp >= 1000:
            return "Gold"
        if xp >= 400:
            return "Silver"
        return "Bronze"

    def _refresh_menu_stats(self) -> None:
        self.menu.update_stats(self.best_score, self.total_xp, self._rank())

    def _play_click(self) -> None:
        try:
            self.audio.play("button")
        except Exception:
            pass

    # -- navigation ---------------------------------------------------------

    def _start_game(self) -> None:
        self.pause_overlay.hide()
        self.stack.setCurrentWidget(self.canvas)
        self.canvas.setFocus()
        self.canvas.start()

    def _open_settings(self) -> None:
        self.settings_widget.mute_cb.blockSignals(True)
        self.settings_widget.mute_cb.setChecked(bool(self.audio.muted))
        self.settings_widget.mute_cb.blockSignals(False)
        self.settings_widget.vol_slider.blockSignals(True)
        self.settings_widget.vol_slider.setValue(int(round(self.audio.volume * 100.0)))
        self.settings_widget.vol_value.setText(f"{int(round(self.audio.volume * 100.0))}%")
        self.settings_widget.vol_slider.blockSignals(False)
        self.stack.setCurrentWidget(self.settings_widget)

    def _close_settings(self) -> None:
        self.stack.setCurrentWidget(self.menu)
        self._refresh_menu_stats()

    def _on_volume_changed(self, v: float) -> None:
        self.volume = float(v)
        try:
            self.settings.setValue("volume", float(v))
        except Exception:
            pass

    def _on_mute_changed(self, m: bool) -> None:
        self.muted = bool(m)
        try:
            self.settings.setValue("muted", bool(m))
        except Exception:
            pass

    def _on_escape(self) -> None:
        if self.stack.currentWidget() is not self.canvas:
            return
        if self.canvas.state == "PLAYING":
            self.canvas.pause()
            self.pause_overlay.setGeometry(0, 0, self.canvas.width(), self.canvas.height())
            self.pause_overlay.show()
            self.pause_overlay.raise_()
        elif self.canvas.state == "PAUSED":
            self._resume_game()

    def _resume_game(self) -> None:
        self.pause_overlay.hide()
        self.canvas.resume()

    def _go_to_menu(self) -> None:
        self.pause_overlay.hide()
        self.canvas.stop()
        self._refresh_menu_stats()
        self.stack.setCurrentWidget(self.menu)

    # -- session end --------------------------------------------------------

    def _compute_xp(self, score: int, correct: int) -> int:
        return max(0, int(score // 10) + int(correct) * 5)

    def _on_session_ended(self, score: int, correct: int, total: int,
                          max_combo: int) -> None:
        xp = self._compute_xp(score, correct)
        self.total_xp += xp
        if score > self.best_score:
            self.best_score = score
        try:
            self.settings.setValue("best_score", int(self.best_score))
            self.settings.setValue("total_xp", int(self.total_xp))
            self.settings.setValue("volume", float(self.volume))
            self.settings.setValue("muted", bool(self.muted))
            self.settings.sync()
        except Exception:
            pass

        self.results.set_results(score, correct, total, max_combo, xp)
        self.stack.setCurrentWidget(self.results)
        self._refresh_menu_stats()

    # -- window events ------------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.pause_overlay is not None:
            self.pause_overlay.setGeometry(0, 0,
                                           self.canvas.width(),
                                           self.canvas.height())

    def closeEvent(self, event) -> None:
        try:
            self.settings.setValue("best_score", int(self.best_score))
            self.settings.setValue("total_xp", int(self.total_xp))
            self.settings.setValue("volume", float(self.volume))
            self.settings.setValue("muted", bool(self.muted))
            self.settings.sync()
        except Exception:
            pass
        try:
            self.canvas.timer.stop()
        except Exception:
            pass
        try:
            self.audio.shutdown()
        except Exception:
            pass
        super().closeEvent(event)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    try:
        app = QApplication(sys.argv)
    except Exception:
        return 1
    app.setApplicationName("Fruit Slash")
    app.setOrganizationName("FruitSlash")
    window = MainWindow()
    window.show()
    code = app.exec()
    cleanup_temp_files()
    return code

if __name__ == "__main__":
    sys.exit(main())