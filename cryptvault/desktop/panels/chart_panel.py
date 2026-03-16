"""
Interactive candlestick chart panel with indicators and pattern overlays.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional
from collections import defaultdict

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from ..theme import (
    ACCENT_BLUE, BB_COLOR, BG_PANEL, CANDLE_DOWN, CANDLE_UP,
    CHART_BG, FONT_SMALL, GRID_COLOR,
    RED, GREEN,
    TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY, VOLUME_DOWN, VOLUME_UP,
    WICK_DOWN, WICK_UP,
)

logger = logging.getLogger(__name__)

CHART_ROWS = [6, 2, 2]   # price, volume, rsi


class ChartPanel(ttk.Frame):
    """Full interactive candlestick chart with indicators and pattern overlays."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._df: Optional[pd.DataFrame] = None
        self._patterns: List[Dict[str, Any]] = []
        self._show_bb = True
        self._show_volume = True
        self._show_rsi = True
        self._show_patterns = True

        self._build_toolbar()
        self._build_figure()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, style="Card.TFrame")
        bar.pack(fill="x", padx=8, pady=(8, 0))

        ttk.Label(bar, text="CHART", style="Title.TLabel").pack(side="left", padx=(4, 16))

        self._indicator_vars: Dict[str, tk.BooleanVar] = {}

        for label, attr in [
            ("BB", "_show_bb"),
            ("Volume", "_show_volume"),
            ("RSI", "_show_rsi"),
            ("Patterns", "_show_patterns"),
        ]:
            var = tk.BooleanVar(value=True)
            self._indicator_vars[attr] = var
            cb = tk.Checkbutton(
                bar,
                text=label,
                variable=var,
                command=lambda a=attr, v=var: self._toggle(a, v),
                bg=BG_PANEL,
                fg=TEXT_SECONDARY,
                activebackground=BG_PANEL,
                activeforeground=TEXT_PRIMARY,
                selectcolor=BG_PANEL,
                relief="flat",
                font=FONT_SMALL,
                cursor="hand2",
            )
            cb.pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", padx=8, fill="y", pady=4)
        ttk.Button(bar, text="Reset Zoom", command=self._reset_zoom, style="TButton").pack(side="left", padx=2)

    def _build_figure(self) -> None:
        fig_frame = ttk.Frame(self, style="Card.TFrame")
        fig_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self._fig = Figure(figsize=(12, 8), facecolor=CHART_BG)
        self._fig.subplots_adjust(left=0.06, right=0.97, top=0.95, bottom=0.06, hspace=0.05)

        gs = GridSpec(sum(CHART_ROWS), 1, figure=self._fig, hspace=0.05)
        self._ax_price = self._fig.add_subplot(gs[:CHART_ROWS[0], 0])
        self._ax_vol   = self._fig.add_subplot(gs[CHART_ROWS[0]:CHART_ROWS[0]+CHART_ROWS[1], 0], sharex=self._ax_price)
        self._ax_rsi   = self._fig.add_subplot(gs[CHART_ROWS[0]+CHART_ROWS[1]:, 0], sharex=self._ax_price)

        for ax in [self._ax_price, self._ax_vol, self._ax_rsi]:
            ax.set_facecolor(CHART_BG)
            ax.tick_params(colors=TEXT_MUTED, labelsize=8)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            for spine in ax.spines.values():
                spine.set_color(GRID_COLOR)

        self._canvas = FigureCanvasTkAgg(self._fig, master=fig_frame)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas.mpl_connect("scroll_event", self._on_scroll)
        self._canvas.mpl_connect("button_press_event", self._on_click)

        self._draw_placeholder()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_chart(
        self,
        df: pd.DataFrame,
        patterns: Optional[List[Dict[str, Any]]] = None,
        symbol: str = "",
    ) -> None:
        """Redraw chart with new data. Safe to call from any thread."""
        self._df = df.copy()
        self._patterns = patterns or []
        self._symbol = symbol
        self._draw()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        if self._df is None or self._df.empty:
            self._draw_placeholder()
            return

        df = self._df.copy()

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        df = df.dropna(subset=["close"])
        if df.empty:
            return

        x = np.arange(len(df))
        closes = df["close"].values
        opens  = df["open"].values   if "open"   in df.columns else closes
        highs  = df["high"].values   if "high"   in df.columns else closes
        lows   = df["low"].values    if "low"    in df.columns else closes
        vols   = df["volume"].values if "volume" in df.columns else np.zeros(len(df))

        for ax in [self._ax_price, self._ax_vol, self._ax_rsi]:
            ax.cla()
            ax.set_facecolor(CHART_BG)
            ax.tick_params(colors=TEXT_MUTED, labelsize=8)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            for spine in ax.spines.values():
                spine.set_color(GRID_COLOR)
            ax.grid(True, color=GRID_COLOR, linewidth=0.4, alpha=0.5)

        # ── Candlesticks ──────────────────────────────────────────────
        width = 0.7
        for i in range(len(df)):
            color = CANDLE_UP if closes[i] >= opens[i] else CANDLE_DOWN
            wick_color = WICK_UP if closes[i] >= opens[i] else WICK_DOWN

            body_bottom = min(opens[i], closes[i])
            body_height = abs(closes[i] - opens[i]) or closes[i] * 0.001

            rect = mpatches.Rectangle(
                (x[i] - width / 2, body_bottom),
                width, body_height,
                facecolor=color, edgecolor=color, linewidth=0.5,
            )
            self._ax_price.add_patch(rect)
            self._ax_price.vlines(x[i], lows[i], highs[i], color=wick_color, linewidth=0.8)

        # ── Bollinger Bands ───────────────────────────────────────────
        if self._show_bb and len(df) >= 20:
            roll = pd.Series(closes).rolling(20)
            bb_mid   = roll.mean().values
            bb_std   = roll.std().values
            bb_upper = bb_mid + 2 * bb_std
            bb_lower = bb_mid - 2 * bb_std
            self._ax_price.plot(x, bb_upper, color=BB_COLOR, linewidth=0.8, linestyle="--", alpha=0.6, label="BB")
            self._ax_price.plot(x, bb_lower, color=BB_COLOR, linewidth=0.8, linestyle="--", alpha=0.6)
            self._ax_price.fill_between(x, bb_lower, bb_upper, alpha=0.05, color=BB_COLOR)

        # ── Pattern overlays ──────────────────────────────────────────
        if self._show_patterns and self._patterns:
            self._draw_patterns(x, df, closes, highs, lows)

        # ── Volume ────────────────────────────────────────────────────
        if self._show_volume:
            vol_colors = [VOLUME_UP if closes[i] >= opens[i] else VOLUME_DOWN for i in range(len(df))]
            self._ax_vol.bar(x, vols, color=vol_colors, width=0.7, edgecolor="none")
            self._ax_vol.set_ylabel("Vol", color=TEXT_MUTED, fontsize=7)

        # ── RSI ───────────────────────────────────────────────────────
        if self._show_rsi and len(df) >= 14:
            rsi = self._calc_rsi(closes, 14)
            self._ax_rsi.plot(x, rsi, color=ACCENT_BLUE, linewidth=1)
            self._ax_rsi.axhline(70, color=RED,   linewidth=0.5, linestyle="--", alpha=0.7)
            self._ax_rsi.axhline(30, color=GREEN, linewidth=0.5, linestyle="--", alpha=0.7)
            self._ax_rsi.fill_between(x, 70, rsi, where=(rsi >= 70), alpha=0.15, color=RED)
            self._ax_rsi.fill_between(x, 30, rsi, where=(rsi <= 30), alpha=0.15, color=GREEN)
            self._ax_rsi.set_ylim(0, 100)
            self._ax_rsi.set_ylabel("RSI", color=TEXT_MUTED, fontsize=7)
            self._ax_rsi.yaxis.set_label_position("right")

        # ── X-axis labels ─────────────────────────────────────────────
        n = len(df)
        tick_step = max(1, n // 8)
        tick_positions = list(range(0, n, tick_step))
        tick_labels = [df.index[i].strftime("%b %d") for i in tick_positions]
        self._ax_rsi.set_xticks(tick_positions)
        self._ax_rsi.set_xticklabels(tick_labels, rotation=0, ha="center", color=TEXT_MUTED, fontsize=7)
        plt.setp(self._ax_price.get_xticklabels(), visible=False)
        plt.setp(self._ax_vol.get_xticklabels(), visible=False)

        # Title
        symbol = getattr(self, "_symbol", "")
        last_price = closes[-1]
        change = (closes[-1] - closes[0]) / closes[0] * 100 if closes[0] != 0 else 0
        sign = "+" if change >= 0 else ""
        self._ax_price.set_title(
            f"{symbol}  ${last_price:,.2f}  {sign}{change:.2f}%",
            color=TEXT_PRIMARY, fontsize=11, loc="left", pad=6, fontweight="bold",
        )

        self._ax_price.set_xlim(-1, n)
        self._ax_price.yaxis.set_label_position("right")
        self._ax_price.yaxis.tick_right()
        self._ax_vol.yaxis.tick_right()
        self._ax_rsi.yaxis.tick_right()

        self._canvas.draw_idle()

    # ------------------------------------------------------------------
    # Pattern Drawing
    # ------------------------------------------------------------------

    def _draw_patterns(
        self, x: np.ndarray, df: pd.DataFrame,
        closes: np.ndarray, highs: np.ndarray, lows: np.ndarray,
    ) -> None:
        """Draw pattern markers and actual geometric shapes on the price chart."""
        n = len(x)
        label_positions: Dict[int, List[str]] = defaultdict(list)

        for pat in self._patterns[:30]:
            idx = pat.get("index", -1)
            if not isinstance(idx, int) or not (0 <= idx < n):
                continue

            name     = pat.get("name", "?")
            bullish  = pat.get("bullish", True)
            color    = GREEN if bullish else RED
            category = pat.get("category", "")
            extra    = pat.get("extra", {})
            target   = pat.get("target")

            # Draw actual shape for chart/reversal/continuation patterns
            if extra:
                self._draw_shape(x, closes, highs, lows, n, name, idx, bullish, color, extra)

            # Marker triangle at pattern bar
            marker = "^" if bullish else "v"
            y_pos = lows[idx] * 0.997 if bullish else highs[idx] * 1.003
            self._ax_price.scatter(
                x[idx], y_pos, color=color, marker=marker, s=60, zorder=5, alpha=0.9
            )
            label_positions[idx].append(name[:12])

            # Dashed target price line for chart patterns
            if target is not None and idx >= n - 40:
                self._ax_price.axhline(
                    target, color=color, linewidth=0.8, linestyle=":",
                    alpha=0.45, label=f"Target {target:.0f}",
                )

        # Text labels (stacked per bar)
        for idx, names in list(label_positions.items())[:15]:
            label = "\n".join(names[:3])
            y_off = -14 if label_positions[idx] else 8
            self._ax_price.annotate(
                label,
                xy=(x[idx], lows[idx]),
                xytext=(2, y_off),
                textcoords="offset points",
                fontsize=5,
                color=TEXT_SECONDARY,
                alpha=0.85,
            )

    def _draw_shape(
        self, x, closes, highs, lows, n,
        name: str, idx: int, bullish: bool, color: str, extra: Dict[str, Any],
    ) -> None:
        """Draw the geometric shape for a chart pattern using stored key points."""

        def xi(i: int) -> int:
            return x[max(0, min(n - 1, i))]

        def safe_close(i: int) -> float:
            return float(closes[max(0, min(n - 1, i))])

        lw = 1.2
        alpha = 0.65

        if name == "Double Top" and "p1" in extra and "p2" in extra:
            p1, p2 = int(extra["p1"]), int(extra["p2"])
            neck = float(extra.get("neck", min(closes[p1:p2+1]) if p1 < p2 else safe_close(p1)))
            # Line connecting two peaks
            self._ax_price.plot([xi(p1), xi(p2)], [safe_close(p1), safe_close(p2)],
                                color=color, lw=lw, alpha=alpha, zorder=4)
            # Neckline horizontal
            self._ax_price.hlines(neck, xi(p1), xi(min(idx + 5, n - 1)),
                                  color=color, lw=lw, linestyle="--", alpha=alpha, zorder=4)

        elif name == "Double Bottom" and "t1" in extra and "t2" in extra:
            t1, t2 = int(extra["t1"]), int(extra["t2"])
            neck = float(extra.get("neck", max(closes[t1:t2+1]) if t1 < t2 else safe_close(t1)))
            self._ax_price.plot([xi(t1), xi(t2)], [safe_close(t1), safe_close(t2)],
                                color=color, lw=lw, alpha=alpha, zorder=4)
            self._ax_price.hlines(neck, xi(t1), xi(min(idx + 5, n - 1)),
                                  color=color, lw=lw, linestyle="--", alpha=alpha, zorder=4)

        elif name in ("Head & Shoulders", "Inverse Head & Shoulders") and "ls" in extra:
            ls   = int(extra["ls"])
            head = int(extra["head"])
            rs   = int(extra["rs"])
            neck = extra.get("neckline")
            # Connect left shoulder → head → right shoulder
            self._ax_price.plot(
                [xi(ls), xi(head), xi(rs)],
                [safe_close(ls), safe_close(head), safe_close(rs)],
                color=color, lw=lw, alpha=alpha, zorder=4,
            )
            if neck is not None:
                self._ax_price.hlines(float(neck), xi(ls), xi(min(idx + 5, n - 1)),
                                      color=color, lw=lw, linestyle="--", alpha=alpha, zorder=4)

        elif name in ("Triple Top", "Triple Bottom") and "p1" in extra:
            pts = [extra.get("p1"), extra.get("p2"), extra.get("p3")]
            valid = [int(p) for p in pts if p is not None and 0 <= int(p) < n]
            if len(valid) >= 2:
                xs = [xi(p) for p in valid]
                ys = [safe_close(p) for p in valid]
                self._ax_price.plot(xs, ys, color=color, lw=lw, alpha=alpha, zorder=4)

        elif name in ("Symmetrical Triangle", "Ascending Triangle", "Descending Triangle",
                      "Rising Wedge", "Falling Wedge") and "start" in extra:
            start = int(extra["start"])
            h_s   = float(extra.get("high_start", safe_close(start)))
            h_e   = float(extra.get("high_end",   safe_close(idx)))
            l_s   = float(extra.get("low_start",  safe_close(start)))
            l_e   = float(extra.get("low_end",    safe_close(idx)))
            self._ax_price.plot([xi(start), xi(idx)], [h_s, h_e],
                                color=color, lw=lw, alpha=alpha, zorder=4)
            self._ax_price.plot([xi(start), xi(idx)], [l_s, l_e],
                                color=color, lw=lw, alpha=alpha, zorder=4)

    def _draw_placeholder(self) -> None:
        for ax in [self._ax_price, self._ax_vol, self._ax_rsi]:
            ax.cla()
            ax.set_facecolor(CHART_BG)
        self._ax_price.text(
            0.5, 0.5, "Enter a symbol and press Analyze",
            transform=self._ax_price.transAxes,
            ha="center", va="center",
            color=TEXT_MUTED, fontsize=13,
        )
        self._canvas.draw_idle()

    # ------------------------------------------------------------------
    # Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_rsi(closes: np.ndarray, period: int = 14) -> np.ndarray:
        deltas = np.diff(closes)
        gains  = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gain = np.convolve(gains,  np.ones(period) / period, mode="full")[:len(closes)]
        avg_loss = np.convolve(losses, np.ones(period) / period, mode="full")[:len(closes)]

        with np.errstate(divide="ignore", invalid="ignore"):
            rs = np.where(avg_loss != 0, avg_gain / avg_loss, 100)
            rsi = 100 - 100 / (1 + rs)

        rsi[:period] = 50
        return rsi

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    def _toggle(self, attr: str, var: tk.BooleanVar) -> None:
        setattr(self, attr, var.get())
        self._draw()

    def _reset_zoom(self) -> None:
        if self._df is not None:
            self._draw()

    def _on_scroll(self, event) -> None:
        if self._df is None:
            return
        ax = self._ax_price
        xmin, xmax = ax.get_xlim()
        span = xmax - xmin
        factor = 0.9 if event.button == "up" else 1.1
        new_span = max(20, min(len(self._df), span * factor))
        centre = (xmin + xmax) / 2
        ax.set_xlim(centre - new_span / 2, centre + new_span / 2)
        self._canvas.draw_idle()

    def _on_click(self, event) -> None:
        pass
