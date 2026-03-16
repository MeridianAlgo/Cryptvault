"""
Analysis panel: ML predictions + pattern list.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional

from ..theme import (
    ACCENT_BLUE, BG_BASE, BG_PANEL, BG_HOVER, BG_BORDER,
    FONT_BODY, FONT_LABEL, FONT_MONO_L, FONT_SMALL, FONT_TINY, FONT_TITLE,
    GREEN, GREEN_DIM, RED, RED_DIM, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY,
    YELLOW, PAD, PAD_SM,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper widgets
# ─────────────────────────────────────────────────────────────────────────────

class _Card(ttk.Frame):
    """Simple card container."""

    def __init__(self, parent, title: str = "", **kw):
        super().__init__(parent, style="Card.TFrame", **kw)
        if title:
            ttk.Label(self, text=title.upper(), style="Title.TLabel").pack(
                anchor="w", padx=PAD, pady=(PAD, PAD_SM)
            )

    def section(self, title: str) -> "ttk.Frame":
        f = ttk.Frame(self, style="Card.TFrame")
        f.pack(fill="x", padx=PAD, pady=2)
        ttk.Label(f, text=title, style="Muted.TLabel", font=FONT_TINY).pack(anchor="w")
        return f


class _Gauge(tk.Canvas):
    """Simple horizontal progress gauge."""

    def __init__(self, parent, value: float = 0.0, color: str = ACCENT_BLUE, height: int = 8, **kw):
        super().__init__(parent, height=height, bg=BG_PANEL, highlightthickness=0, **kw)
        self._color = color
        self._value = 0.0
        self.bind("<Configure>", lambda e: self._draw())
        self.set(value)

    def set(self, value: float) -> None:
        self._value = max(0.0, min(1.0, value))
        self._draw()

    def _draw(self) -> None:
        w = self.winfo_width() or 200
        h = self.winfo_height() or 8
        self.delete("all")
        r = h // 2
        # Track
        self.create_rounded_rectangle(0, 0, w, h, r, fill=BG_HOVER)
        # Fill
        fill_w = max(r * 2, int(w * self._value))
        self.create_rounded_rectangle(0, 0, fill_w, h, r, fill=self._color)

    def create_rounded_rectangle(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
               x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kw)


# ─────────────────────────────────────────────────────────────────────────────
# Prediction Card
# ─────────────────────────────────────────────────────────────────────────────

class PredictionCard(_Card):
    """ML prediction summary card."""

    def __init__(self, parent, **kw):
        super().__init__(parent, title="ML Prediction", **kw)
        self._build()

    def _build(self) -> None:
        body = ttk.Frame(self, style="Card.TFrame")
        body.pack(fill="x", padx=PAD, pady=PAD_SM)

        # Price prediction row
        price_row = ttk.Frame(body, style="Card.TFrame")
        price_row.pack(fill="x", pady=2)
        ttk.Label(price_row, text="Predicted Price", style="Card.TLabel",
                  foreground=TEXT_SECONDARY, font=FONT_SMALL).pack(side="left")
        self._lbl_price = ttk.Label(price_row, text="—", style="BigPrice.TLabel")
        self._lbl_price.pack(side="right")

        # Direction
        dir_row = ttk.Frame(body, style="Card.TFrame")
        dir_row.pack(fill="x", pady=2)
        ttk.Label(dir_row, text="Direction", style="Card.TLabel",
                  foreground=TEXT_SECONDARY, font=FONT_SMALL).pack(side="left")
        self._lbl_dir = ttk.Label(dir_row, text="—", style="Card.TLabel", font=FONT_LABEL)
        self._lbl_dir.pack(side="right")

        # Confidence gauge
        ttk.Label(body, text="Confidence", style="Card.TLabel",
                  foreground=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w", pady=(4, 0))
        self._gauge = _Gauge(body, width=300)
        self._gauge.pack(fill="x", pady=(2, 0))
        self._lbl_conf = ttk.Label(body, text="0%", style="Card.TLabel",
                                    foreground=TEXT_MUTED, font=FONT_TINY)
        self._lbl_conf.pack(anchor="e")

        # MAPE / error
        ttk.Separator(body).pack(fill="x", pady=6)
        meta_row = ttk.Frame(body, style="Card.TFrame")
        meta_row.pack(fill="x")
        for key in ("mape_lbl", "horizon_lbl", "model_lbl"):
            lbl = ttk.Label(meta_row, text="—", style="Card.TLabel",
                            foreground=TEXT_MUTED, font=FONT_TINY)
            lbl.pack(side="left", expand=True)
            setattr(self, f"_{key}", lbl)

    def update(self, prediction: Optional[Dict[str, Any]]) -> None:
        if not prediction:
            self._lbl_price.config(text="—")
            self._lbl_dir.config(text="—", foreground=TEXT_SECONDARY)
            self._gauge.set(0)
            self._lbl_conf.config(text="0%")
            return

        price = prediction.get("predicted_price") or prediction.get("price")
        direction = prediction.get("direction", "NEUTRAL").upper()
        confidence = float(prediction.get("confidence", 0.5))
        mape = prediction.get("mape")
        horizon = prediction.get("horizon", "1d")
        model = prediction.get("model", "Ensemble")

        if price:
            self._lbl_price.config(text=f"${float(price):,.2f}")

        color = GREEN if direction == "UP" else (RED if direction == "DOWN" else TEXT_SECONDARY)
        arrow = "↑" if direction == "UP" else ("↓" if direction == "DOWN" else "→")
        self._lbl_dir.config(text=f"{arrow} {direction}", foreground=color)

        gauge_color = GREEN if direction == "UP" else (RED if direction == "DOWN" else ACCENT_BLUE)
        self._gauge.set(confidence)
        self._gauge._color = gauge_color
        self._gauge._draw()
        self._lbl_conf.config(text=f"{confidence * 100:.0f}%")

        self._mape_lbl.config(text=f"MAPE: {mape:.2f}%" if mape else "MAPE: —")
        self._horizon_lbl.config(text=f"Horizon: {horizon}")
        self._model_lbl.config(text=f"Model: {model}")


# ─────────────────────────────────────────────────────────────────────────────
# Pattern List
# ─────────────────────────────────────────────────────────────────────────────

class PatternListPanel(_Card):
    """Scrollable list of detected patterns with badges."""

    def __init__(self, parent, **kw):
        super().__init__(parent, title="Detected Patterns", **kw)
        self._build()

    def _build(self) -> None:
        # Summary row
        self._summary_frame = ttk.Frame(self, style="Card.TFrame")
        self._summary_frame.pack(fill="x", padx=PAD, pady=(0, PAD_SM))
        self._lbl_count  = ttk.Label(self._summary_frame, text="0 patterns", style="Card.TLabel",
                                      foreground=TEXT_MUTED, font=FONT_SMALL)
        self._lbl_count.pack(side="left")
        self._lbl_signal = ttk.Label(self._summary_frame, text="", style="Card.TLabel",
                                      font=FONT_LABEL)
        self._lbl_signal.pack(side="right")

        # Scrollable list
        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        scrollbar = ttk.Scrollbar(container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self._canvas = tk.Canvas(container, bg=BG_PANEL, highlightthickness=0,
                                  yscrollcommand=scrollbar.set)
        self._canvas.pack(fill="both", expand=True)
        scrollbar.config(command=self._canvas.yview)

        self._list_frame = ttk.Frame(self._canvas, style="Card.TFrame")
        self._canvas_window = self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")

        self._list_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update(self, patterns: List[Dict[str, Any]]) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        if not patterns:
            ttk.Label(self._list_frame, text="No patterns detected",
                      style="Card.TLabel", foreground=TEXT_MUTED, font=FONT_SMALL).pack(pady=20)
            self._lbl_count.config(text="0 patterns")
            self._lbl_signal.config(text="")
            return

        bullish = sum(1 for p in patterns if p.get("bullish", p.get("direction", "").lower() == "bullish"))
        bearish = len(patterns) - bullish

        self._lbl_count.config(text=f"{len(patterns)} patterns found")
        if bullish > bearish:
            self._lbl_signal.config(text=f"↑ {bullish}B / {bearish}S", foreground=GREEN)
        elif bearish > bullish:
            self._lbl_signal.config(text=f"↓ {bullish}B / {bearish}S", foreground=RED)
        else:
            self._lbl_signal.config(text=f"→ Mixed", foreground=YELLOW)

        for pat in patterns:
            self._add_pattern_row(pat)

    def _add_pattern_row(self, pat: Dict[str, Any]) -> None:
        name = pat.get("name") or pat.get("pattern_type") or pat.get("type", "Unknown")
        desc = pat.get("description") or pat.get("signal", "")
        category = str(pat.get("category", "")).upper()
        bullish = pat.get("bullish", pat.get("direction", "").lower() == "bullish")
        strength = float(pat.get("strength", pat.get("confidence", 0.5)))

        bg = GREEN_DIM if bullish else RED_DIM
        fg = GREEN if bullish else RED
        tag = "BULL" if bullish else "BEAR"

        row = tk.Frame(self._list_frame, bg=bg, pady=3)
        row.pack(fill="x", pady=1, ipady=4, ipadx=6)

        # Tag badge
        badge = tk.Label(row, text=tag, bg=fg, fg="#000", font=FONT_TINY,
                         padx=4, pady=1, relief="flat")
        badge.pack(side="left", padx=(6, 8))

        # Name + desc
        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=name, bg=bg, fg=TEXT_PRIMARY, font=FONT_LABEL,
                 anchor="w").pack(anchor="w")
        if desc:
            tk.Label(info, text=desc[:80], bg=bg, fg=TEXT_SECONDARY, font=FONT_TINY,
                     anchor="w").pack(anchor="w")

        # Category + strength
        right = tk.Frame(row, bg=bg)
        right.pack(side="right", padx=6)
        if category:
            tk.Label(right, text=category[:12], bg=bg, fg=TEXT_MUTED, font=FONT_TINY).pack(anchor="e")
        tk.Label(right, text=f"{strength * 100:.0f}%", bg=bg, fg=fg, font=FONT_SMALL).pack(anchor="e")


# ─────────────────────────────────────────────────────────────────────────────
# Combined Analysis Panel
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisPanel(ttk.Frame):
    """Combined analysis panel: prediction + patterns."""

    def __init__(self, parent, **kw):
        super().__init__(parent, style="TFrame", **kw)
        self._build()

    def _build(self) -> None:
        # ML Prediction card (top)
        self.prediction_card = PredictionCard(self)
        self.prediction_card.pack(fill="x", padx=4, pady=4)

        # Pattern list (fills remaining space)
        self.pattern_list = PatternListPanel(self)
        self.pattern_list.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def update(
        self,
        prediction: Optional[Dict[str, Any]] = None,
        patterns: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.prediction_card.update(prediction)
        self.pattern_list.update(patterns or [])
