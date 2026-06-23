"""
EVE Local Watch — danger detector for EVE Online local chat.
Requirements: pip install mss pillow numpy sounddevice plyer pyautogui
"""

import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import mss
from PIL import Image
import sounddevice as sd
import json, os, sys

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


# ─────────────────────────────────────────────
#  EMBEDDED ICON  (ship, base64 PNG)
# ─────────────────────────────────────────────
_ICON_32 = "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"
_ICON_22 = "iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAADlElEQVR4nIWVTW8bVRSGn3Pn246x63w4aWggdavQBUEUhU1BQghViAWCDaqQ2CB+BqyQwg9BYhEk1C0LBAKhFiGRLlBVSEhCS4rjfJE4sWfsmTksxolt6oRZzL0z95z3vPe955wrxdKzypmPdMezTAQBFO1ayqmL+X/AYaC9de2un7xVQVXPAj7vkTOCDf49A7jPRAwgiFiIdM1FhnqdhAWwzydnSDstxNgknQhQjOOjaYzlBKimQyjp+cBi2XQau1RuvE/abtLefwxicEtTGDdg68cvcAqjaBI/wVnkDGARQeMOXmmS8YW3aWzcI6hUATBejtz0Nfbvf0saHiHGHsp8uMZiiFsHjC28Q2N9GbdYwXIDxNjY+RLHG8uML7xL3Gp0M2xQ8yFZIYgYkvCIqdc+JImaiO0ils3B6k80Nn5BxMI4Pml0xMXXPyIJj8FIn38WaABYBNKkg1usMPriW0Q7f+IWJ2htrWEcH+P4hNvruMUJwp2HlOdv4hYraNxBpI/3oMYCYpFGhxTmb9KsrWAcD8sNGJmZx85dABR/bAYRMI5Pq7ZCofoyOz9/hT1ShjT5r8ZZLE0T7HyJYLJKMFGlOPcK7YNtgskrNP/+nVZthWDyKtHeJqW5GwSTV8hNXcXOl9GkB4qCnPQKYzl0jnYpv/Amlp/HG71EbvoaSfMATTrEzUNQxR4pYQclRITjx78R7T0iCY/Yvfc1bmEUTeMeYzEWcdjAG5uhMHud3MXnqN/5kmjnEXa+TLO2Sv3OEvW7SxxvPsA4HuHeX9TvLpGbmqMw+xL+2Axx2MgqVUFKFy5rGke4T40z+96nRHub1H74nNbWH4jlkIQNqrc+w/JzoErcOmJt6WMsv4AmHYJKlalXP8ArT7O29Antw22M42FO+sLlW4s0ayts3F4krK9jeXmM4yGWwz8PvscffRq3OMHer99gbC87WC9PWF9n4/Yirdoq1VuLfRoXn1HLDfDGLtFYX8by8ohlQ5qCZMkuls3o82+QdNrs3/8OVLM+pIAxaBqThMcUZq8T7jwkbbeQUmlWVZU0jrC8bLuo9pJFszGJmgCZTZdVX0JlDStqIo6HiGR5LEaw3ABN08yuC6ja87P8kWySpl1cPam1bqqmGDc4jWj3LgPtVY7SdzNI9yJJT6sz21AXUPUUXjXNZgOV98T1NryZ96vUi3Qy7fnYg2A9GU4Pp1+agc+uFNpHQHu2/wJ1XW7eaaIVZwAAAABJRU5ErkJggg=="

def _photo(b64, master):
    import tkinter as tk
    from PIL import Image as _I, ImageTk
    import base64, io
    img = _I.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
    return ImageTk.PhotoImage(img, master=master)

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
DEFAULT_CONFIG = {
    "region_x": 0.0895, "region_y": 0.4944,
    "region_w": 0.0254, "region_h": 0.0354,
    "interval": 1.0,
    "alert_repeat": 0,          # 0 = no repeat; >0 = repeat every N seconds
    "blue_ranges": [
        {"r": [0,   70],  "g": [20,  90],  "b": [70,  160]},   # dark blue bg (gap closed to 90)
        {"r": [55,  115], "g": [75,  125], "b": [125, 165]},   # mid blue transition
        {"r": [60,  115], "g": [80,  130], "b": [125, 165]},   # mid blue variant
        {"r": [20,  130], "g": [70,  180], "b": [140, 255]},   # light/fleet blue bg (lowered to 70/140)
        {"r": [15,  80],  "g": [75,  160], "b": [15,  80]},
        {"r": [40,  120], "g": [55,  160], "b": [40,  120]},
        {"r": [50,  155], "g": [0,   65],  "b": [85,  205]},
        {"r": [80,  175], "g": [30,  100], "b": [115, 210]},
    ],
    "tone_freq": 880, "tone_duration": 0.4, "tone_volume": 0.35,
    "min_danger_pixels": 5,
}

if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(_BASE, "config.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                saved = json.load(f)
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(saved)
            return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


# ─────────────────────────────────────────────
#  DETECTION
# ─────────────────────────────────────────────
def _build_masks(img_rgb, blue_ranges):
    r = img_rgb[:, :, 0].astype(int)
    g = img_rgb[:, :, 1].astype(int)
    b = img_rgb[:, :, 2].astype(int)
    brightness  = (r + g + b) / 3
    background  = brightness < 50
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    grey = (cmax - cmin) < 45
    friendly = np.zeros(r.shape, dtype=bool)
    for rng in blue_ranges:
        friendly |= (
            (r >= rng["r"][0]) & (r <= rng["r"][1]) &
            (g >= rng["g"][0]) & (g <= rng["g"][1]) &
            (b >= rng["b"][0]) & (b <= rng["b"][1])
        )
    danger = ~background & ~grey & ~friendly
    return danger

def count_danger_pixels(img_rgb, blue_ranges):
    return int(np.count_nonzero(_build_masks(img_rgb, blue_ranges)))


# ─────────────────────────────────────────────
#  SOUND & NOTIFICATION
# ─────────────────────────────────────────────
def play_alert(freq=880, duration=0.4, volume=0.35):
    sr   = 44100
    t    = np.linspace(0, duration, int(sr * duration), False)
    tone = volume * np.sin(2 * np.pi * freq * t)
    fade = np.linspace(1, 0, min(int(sr * 0.05), len(tone)))
    tone[-len(fade):] *= fade
    sd.play(tone, sr, blocking=False)


def send_notification(title, message):
    if HAS_PLYER:
        try:
            notification.notify(title=title, message=message,
                                app_name="EVE Local Watch", timeout=4)
        except Exception:
            pass


# ─────────────────────────────────────────────
#  MONITOR THREAD
# ─────────────────────────────────────────────
class Monitor:
    def __init__(self, cfg, status_cb, danger_cb, preview_cb=None):
        self.cfg          = cfg
        self.status_cb    = status_cb
        self.danger_cb    = danger_cb
        self.preview_cb   = preview_cb
        self._running     = False
        self._last_danger = False
        self._last_alert  = 0.0   # timestamp of last played alert

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False

    def _region(self, mon):
        c = self.cfg
        return {
            "left":   int(mon["width"]  * c["region_x"]),
            "top":    int(mon["height"] * c["region_y"]),
            "width":  int(mon["width"]  * c["region_w"]),
            "height": int(mon["height"] * c["region_h"]),
        }

    def _loop(self):
        self.status_cb("starting")
        with mss.mss() as sct:
            mon    = sct.monitors[1]
            region = self._region(mon)
            while self._running:
                try:
                    raw    = sct.grab(region)
                    img    = np.array(Image.frombytes("RGB", raw.size, raw.rgb))
                    dp     = count_danger_pixels(img, self.cfg["blue_ranges"])
                    if self.preview_cb:
                        self.preview_cb(img, self.cfg["blue_ranges"])
                    danger = dp >= self.cfg["min_danger_pixels"]

                    if danger:
                        self.status_cb(("danger", dp))
                        now    = time.time()
                        repeat = self.cfg.get("alert_repeat", 0)
                        # Fire on rising edge OR when repeat interval has elapsed
                        if not self._last_danger or (
                                repeat > 0 and (now - self._last_alert) >= repeat):
                            play_alert(self.cfg["tone_freq"],
                                       self.cfg["tone_duration"],
                                       self.cfg["tone_volume"])
                            send_notification("⚠️ EVE Local Watch",
                                              "Non-blue player in local!")
                            self._last_alert = now
                        if not self._last_danger:
                            self.danger_cb(True)
                    else:
                        self.status_cb(("clear", dp))
                        if self._last_danger:
                            self.danger_cb(False)
                            self._last_alert = 0.0

                    self._last_danger = danger
                except Exception as e:
                    self.status_cb(("error", str(e)))
                time.sleep(self.cfg["interval"])
        self.status_cb("stopped")


# ─────────────────────────────────────────────
#  CALIBRATION WINDOW
# ─────────────────────────────────────────────
class CalibrationWindow(tk.Toplevel):
    def __init__(self, parent):
        try:
            import ctypes
            # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 — works on all Windows 10+ scales
            ctypes.windll.user32.SetProcessDpiAwarenessContext(
                ctypes.c_ssize_t(-4))  # -4 = PER_MONITOR_V2
        except Exception:
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                pass
        try:
            import pyautogui
            self._screen_w, self._screen_h = pyautogui.size()
            screenshot = pyautogui.screenshot()
        except ImportError:
            messagebox.showerror("Missing library",
                "pyautogui is not installed.\n\nRun: pip install pyautogui")
            return

        super().__init__(parent)
        self.parent  = parent
        self._clicks = []
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.configure(cursor="crosshair")

        from PIL import ImageTk
        self._img_tk = ImageTk.PhotoImage(screenshot)
        self._canvas = tk.Canvas(self, width=self._screen_w,
                                 height=self._screen_h, highlightthickness=0)
        self._canvas.pack()
        self._canvas.create_image(0, 0, anchor="nw", image=self._img_tk)
        self._label = tk.Label(self,
            text="  Step 1/2 — Click the TOP-LEFT corner of the icon column  ",
            bg="#f0c040", fg="#000", font=("Segoe UI", 14, "bold"))
        self._label.place(x=10, y=10)
        self.bind("<Escape>", lambda e: self.destroy())
        self._canvas.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        x, y = event.x, event.y
        self._clicks.append((x, y))
        r = 6
        self._canvas.create_oval(x-r, y-r, x+r, y+r,
                                  fill="#ff3333", outline="white", width=2)
        if len(self._clicks) == 1:
            self._label.config(
                text="  Step 2/2 — Click the BOTTOM-RIGHT corner of the icon column  ")
        elif len(self._clicks) == 2:
            x1, y1 = self._clicks[0]
            x2, y2 = self._clicks[1]
            sw, sh  = self._screen_w, self._screen_h
            rx = round(x1 / sw, 4); ry = round(y1 / sh, 4)
            rw = round((x2 - x1) / sw, 4); rh = round((y2 - y1) / sh, 4)
            self._canvas.create_rectangle(x1, y1, x2, y2,
                                           outline="#ff3333", width=2)
            self._label.config(text="  ✅ Done — closing…  ")
            self.update()
            self.after(900, lambda: self._apply(rx, ry, rw, rh))

    def _apply(self, rx, ry, rw, rh):
        self.parent._rx.set(str(rx)); self.parent._ry.set(str(ry))
        self.parent._rw.set(str(rw)); self.parent._rh.set(str(rh))
        self.destroy()


# ─────────────────────────────────────────────
#  PREVIEW WINDOW
# ─────────────────────────────────────────────
class PreviewWindow(tk.Toplevel):
    MAX_W = 600   # max window width
    MAX_H = 800   # max window height
    MIN_SCALE = 2 # minimum zoom so a 1px-wide region is still visible

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Pixel Preview")
        self.configure(bg="#0d0d1a")
        self.resizable(True, True)
        self.attributes("-topmost", True)
        self._closed   = False
        self._img_ref  = None
        self._sized    = False   # have we auto-sized yet?

        tk.Label(self, text="REGION PREVIEW",
                 font=("Segoe UI", 9, "bold"), bg="#0d0d1a", fg="#4a9eff").pack(pady=(6,0))
        tk.Label(self, text="🔴 danger   ·   original = safe",
                 font=("Segoe UI", 8), bg="#0d0d1a", fg="#555577").pack()
        self._canvas = tk.Canvas(self, bg="#0d0d1a", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True, padx=6, pady=6)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self._closed = True
        self.destroy()

    def update_frame(self, img_rgb, blue_ranges):
        if self._closed or not self.winfo_exists():
            return
        from PIL import Image as PilImage, ImageTk

        mask = _build_masks(img_rgb, blue_ranges)
        ann  = img_rgb.copy()
        ann[mask] = [255, 40, 40]

        src_h, src_w = ann.shape[:2]

        # On first frame: auto-size the window so the full region fits.
        # Pick the largest integer scale that stays within MAX_W x MAX_H.
        if not self._sized:
            scale = self.MIN_SCALE
            while True:
                next_s = scale + 1
                if (src_w * next_s <= self.MAX_W and
                        src_h * next_s <= self.MAX_H):
                    scale = next_s
                else:
                    break
            win_w = max(src_w * scale + 12, 160)
            win_h = max(src_h * scale + 50, 120)   # +50 for labels
            self.geometry(f"{win_w}x{win_h}")
            self._sized = True

        # Render: fill whatever the canvas currently is
        cw = self._canvas.winfo_width()  or (self.winfo_width() - 12)
        ch = self._canvas.winfo_height() or (self.winfo_height() - 50)
        if cw < 2 or ch < 2:
            return

        scale = max(min(cw / max(src_w, 1), ch / max(src_h, 1)), self.MIN_SCALE)
        nw, nh = int(src_w * scale), int(src_h * scale)

        scaled = PilImage.fromarray(ann.astype(np.uint8)).resize(
            (nw, nh), PilImage.NEAREST)
        self._img_ref = ImageTk.PhotoImage(scaled)
        self._canvas.delete("all")
        self._canvas.create_image(cw // 2, ch // 2, anchor="center",
                                  image=self._img_ref)


# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
BG      = "#0f0f1a"
BG2     = "#161625"
BG3     = "#1e1e32"
ACCENT  = "#4a9eff"
FG      = "#d0d8f0"
FG2     = "#6070a0"
DANGER_C= "#ff4455"
SAFE_C  = "#44cc88"
ENTRY   = "#0a0a18"
BTN     = "#1a2038"
BTN_HOV = "#253060"


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg             = load_config()
        self.monitor         = None
        self.running         = False
        self._preview_window = None

        self.title("EVE Local Watch")
        self.resizable(False, False)
        self.configure(bg=BG)
        try:
            # Try loading the .ico file first (best quality, used by Windows for taskbar)
            import sys, os
            if getattr(sys, 'frozen', False):
                # PyInstaller extracts bundled data to sys._MEIPASS
                ico = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass
        try:
            self._wm_icon = _photo(_ICON_32, self)
            self.iconphoto(True, self._wm_icon)
        except Exception:
            pass
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── BUILD ─────────────────────────────────
    def _build_ui(self):
        P = 12   # outer padding

        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG, padx=P, pady=10)
        hdr.pack(fill="x")
        self._icon_img = _photo(_ICON_22, self)
        tk.Label(hdr, image=self._icon_img, bg=BG
                 ).pack(side="left", padx=(0, 8))
        tf = tk.Frame(hdr, bg=BG)
        tf.pack(side="left")
        tk.Label(tf, text="EVE Local Watch", font=("Segoe UI", 13, "bold"),
                 bg=BG, fg=FG).pack(anchor="w")
        tk.Label(tf, text="Local chat danger detector", font=("Segoe UI", 8),
                 bg=BG, fg=FG2).pack(anchor="w")

        # ── Status banner ────────────────────────────────────────────────────
        self._banner = tk.Frame(self, bg=BG3, padx=P, pady=7)
        self._banner.pack(fill="x")
        self._dot = tk.Label(self._banner, text="●", font=("Segoe UI", 13),
                             bg=BG3, fg=FG2)
        self._dot.pack(side="left", padx=(0, 7))
        self._status_var = tk.StringVar(value="Idle — press Start")
        tk.Label(self._banner, textvariable=self._status_var,
                 font=("Segoe UI", 9), bg=BG3, fg=FG, anchor="w"
                 ).pack(side="left", fill="x", expand=True)

        # ── START / STOP ─────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=BG, padx=P, pady=8)
        ctrl.pack(fill="x")
        self.start_btn = self._bigbtn(ctrl, "▶  START", SAFE_C,   self._start)
        self.stop_btn  = self._bigbtn(ctrl, "■  STOP",  DANGER_C, self._stop)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.stop_btn.pack( side="left", expand=True, fill="x", padx=(4, 0))
        self.stop_btn.config(state="disabled")

        tk.Frame(self, bg=BG3, height=1).pack(fill="x")

        # ── TWO-COLUMN BODY ──────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG, padx=P, pady=10)
        body.pack(fill="both", expand=True)
        left  = tk.Frame(body, bg=BG)
        right = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # LEFT COLUMN ────────────────────────────────────────────────────────

        # Screen Region card
        rc = self._card(left, "📐  Screen Region")
        self._rx = self._field(rc, "X start", self.cfg["region_x"])
        self._ry = self._field(rc, "Y start", self.cfg["region_y"])
        self._rw = self._field(rc, "Width",   self.cfg["region_w"])
        self._rh = self._field(rc, "Height",  self.cfg["region_h"])
        btns_r = tk.Frame(rc, bg=BG2)
        btns_r.pack(fill="x", pady=(8, 0))
        self._obtn(btns_r, "🎯 Calibrate", self._open_calibration
                   ).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._obtn(btns_r, "💾 Save",      self._save
                   ).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # Scan interval card
        ic = self._card(left, "⏱  Scan Interval")
        irow = tk.Frame(ic, bg=BG2)
        irow.pack(fill="x")
        self._interval_var = tk.DoubleVar(value=self.cfg["interval"])
        tk.Spinbox(irow, from_=0.2, to=10.0, increment=0.1,
                   textvariable=self._interval_var,
                   format="%.1f", width=5,
                   bg=ENTRY, fg=FG, buttonbackground=BTN,
                   relief="flat", font=("Segoe UI", 10),
                   highlightthickness=1, highlightcolor=ACCENT,
                   highlightbackground=BG3
                   ).pack(side="left", ipady=3)
        tk.Label(irow, text="sec", bg=BG2, fg=FG2,
                 font=("Segoe UI", 9)).pack(side="left", padx=6)

        # RIGHT COLUMN ───────────────────────────────────────────────────────

        # Alert Tone card
        ac = self._card(right, "🔊  Alert Tone")
        self._freq = self._field(ac, "Freq (Hz)", self.cfg["tone_freq"])
        self._vol  = self._field(ac, "Volume",    self.cfg["tone_volume"])
        self._obtn(ac, "▶ Test tone", self._test_tone).pack(fill="x", pady=(6, 0))

        # Repeat alert card
        rpc = self._card(right, "🔁  Alert Repeat")
        tk.Label(rpc, text="Repeat while danger persists  (0 = off)",
                 bg=BG2, fg=FG2, font=("Segoe UI", 8)).pack(anchor="w", pady=(0,5))

        rp_row = tk.Frame(rpc, bg=BG2)
        rp_row.pack(fill="x")
        self._repeat_var = tk.IntVar(value=int(self.cfg.get("alert_repeat", 0)))
        self._repeat_var.trace_add("write", self._on_repeat_change)
        tk.Spinbox(rp_row, from_=0, to=30, increment=1,
                   textvariable=self._repeat_var,
                   format="%2.0f", width=4,
                   bg=ENTRY, fg=ACCENT, buttonbackground=BTN,
                   relief="flat", font=("Segoe UI", 11, "bold"),
                   highlightthickness=1, highlightcolor=ACCENT,
                   highlightbackground=BG3
                   ).pack(side="left", ipady=3)
        tk.Label(rp_row, text="seconds  (0 = off)",
                 bg=BG2, fg=FG2, font=("Segoe UI", 9)).pack(side="left", padx=8)

        # Sensitivity card
        sc = self._card(right, "🎚  Sensitivity")
        self._mindp = self._field(sc, "Min pixels", self.cfg["min_danger_pixels"])
        tk.Label(sc, text="Raise to reduce false positives",
                 bg=BG2, fg=FG2, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        # ── Bottom row ───────────────────────────────────────────────────────
        tk.Frame(self, bg=BG3, height=1).pack(fill="x")
        bot = tk.Frame(self, bg=BG, padx=P, pady=8)
        bot.pack(fill="x")
        self._obtn(bot, "🔍 Pixel preview", self._open_preview
                   ).pack(side="left", expand=True, fill="x")

    # ── WIDGET HELPERS ────────────────────────
    def _card(self, parent, title):
        f = tk.Frame(parent, bg=BG2, padx=9, pady=8,
                     highlightthickness=1, highlightbackground=BG3)
        f.pack(fill="x", pady=(0, 8))
        tk.Label(f, text=title, font=("Segoe UI", 9, "bold"),
                 bg=BG2, fg=ACCENT).pack(anchor="w", pady=(0, 5))
        return f

    def _field(self, parent, label, default):
        row = tk.Frame(parent, bg=BG2)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=BG2, fg=FG2,
                 font=("Segoe UI", 9), width=9, anchor="w").pack(side="left")
        var = tk.StringVar(value=str(default))
        tk.Entry(row, textvariable=var, width=9,
                 bg=ENTRY, fg=FG, insertbackground=FG, relief="flat",
                 font=("Segoe UI", 9),
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BG3
                 ).pack(side="left", ipady=3)
        return var

    def _bigbtn(self, parent, text, colour, cmd):
        return tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                         bg=BTN, fg=colour, activebackground=BTN_HOV,
                         activeforeground=colour, relief="flat",
                         cursor="hand2", padx=8, pady=8, command=cmd)

    def _obtn(self, parent, text, cmd):
        return tk.Button(parent, text=text, font=("Segoe UI", 9),
                         bg=BG2, fg=FG, activebackground=BTN_HOV,
                         activeforeground=FG, relief="flat",
                         cursor="hand2", padx=6, pady=5, command=cmd,
                         highlightthickness=1, highlightbackground=BG3)

    # ── CALIBRATION / PREVIEW ─────────────────
    def _on_repeat_change(self, *_):
        """Push repeat interval into running monitor immediately — no restart needed."""
        try:
            val = int(self._repeat_var.get())
            self.cfg["alert_repeat"] = val
            if self.monitor:
                self.monitor.cfg["alert_repeat"] = val
        except (ValueError, tk.TclError):
            pass

    def _open_calibration(self):
        CalibrationWindow(self)

    def _open_preview(self):
        if self._preview_window and not self._preview_window._closed:
            self._preview_window.lift()
            return
        self._preview_window = PreviewWindow(self)

    def _send_preview(self, img, blue_ranges):
        if self._preview_window and not self._preview_window._closed:
            self.after(0, lambda: self._preview_window.update_frame(img, blue_ranges))

    # ── CONFIG ────────────────────────────────
    def _collect(self):
        try:
            self.cfg["region_x"]          = float(self._rx.get())
            self.cfg["region_y"]          = float(self._ry.get())
            self.cfg["region_w"]          = float(self._rw.get())
            self.cfg["region_h"]          = float(self._rh.get())
            self.cfg["interval"]          = round(float(self._interval_var.get()), 1)
            self.cfg["tone_freq"]         = int(self._freq.get())
            self.cfg["tone_volume"]       = float(self._vol.get())
            self.cfg["min_danger_pixels"] = int(self._mindp.get())
            self.cfg["alert_repeat"]      = int(self._repeat_var.get())
            return True
        except ValueError as e:
            messagebox.showerror("Config error", str(e))
            return False

    def _test_tone(self):
        if self._collect():
            play_alert(self.cfg["tone_freq"], 0.3, self.cfg["tone_volume"])

    def _save(self):
        if self._collect():
            save_config(self.cfg)
            self._set_status_text("💾  Settings saved.", FG2)

    def _start(self):
        if not self._collect():
            return
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.monitor = Monitor(self.cfg, self._on_status, self._on_danger,
                               preview_cb=self._send_preview)
        self.monitor.start()

    def _stop(self):
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._set_idle()

    # ── STATUS CALLBACKS ──────────────────────
    def _set_idle(self):
        self._dot.config(fg=FG2)
        self._status_var.set("Idle — press Start")
        self._set_banner_bg(BG3)

    def _set_status_text(self, msg, colour=FG):
        self._status_var.set(msg)
        self._dot.config(fg=colour)

    def _set_banner_bg(self, colour):
        self._banner.config(bg=colour)
        for w in self._banner.winfo_children():
            try: w.config(bg=colour)
            except: pass

    def _on_status(self, msg):
        def _u():
            if msg == "starting":
                self._dot.config(fg="#ffcc00")
                self._status_var.set("Starting…")
                self._set_banner_bg(BG3)
            elif msg == "stopped":
                self._set_idle()
            elif isinstance(msg, tuple):
                kind, val = msg
                if kind == "danger":
                    self._dot.config(fg=DANGER_C)
                    self._status_var.set(f"⚠  DANGER — {val} suspect pixels")
                    self._set_banner_bg("#2a0010")
                elif kind == "clear":
                    self._dot.config(fg=SAFE_C)
                    self._status_var.set(f"✔  Clear — {val} pixels")
                    self._set_banner_bg(BG3)
                elif kind == "error":
                    self._dot.config(fg="#ff8800")
                    self._status_var.set(f"Error: {val}")
        self.after(0, _u)

    def _on_danger(self, is_danger):
        bg = "#1a0008" if is_danger else BG
        self.after(0, lambda: self.configure(bg=bg))

    def _on_close(self):
        self._stop()
        self.destroy()


if __name__ == "__main__":
    # Set DPI awareness before creating any windows
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_ssize_t(-4))
    except Exception:
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    App().mainloop()
