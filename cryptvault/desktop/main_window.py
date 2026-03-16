"""
CryptVault Desktop Application - Main Window
A modern, dark-themed trading analysis desktop app.
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional

from .theme import (
    ACCENT_BLUE, BG_DEEP, BG_PANEL, BG_BORDER, BG_HOVER,
    FONT_BODY, FONT_SMALL, FONT_TINY,
    GREEN, RED, SIDEBAR_WIDTH, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY,
    TOPBAR_HEIGHT, YELLOW, apply_ttk_theme,
)
from .panels.chart_panel import ChartPanel
from .panels.analysis_panel import AnalysisPanel

logger = logging.getLogger(__name__)

TIMEFRAMES = [
    ("1D",  "1d",   "1d"),
    ("5D",  "5d",   "1h"),
    ("1M",  "30d",  "1d"),
    ("3M",  "90d",  "1d"),
    ("6M",  "180d", "1d"),
    ("1Y",  "365d", "1d"),
    ("2Y",  "730d", "1wk"),
]

NAV_ITEMS = [
    ("Chart",    "chart"),
    ("Analysis", "analysis"),
]


class MainWindow:
    """CryptVault main application window."""

    def __init__(self):
        self._current_symbol = "BTC-USD"
        self._current_tf_idx = 2       # "1M" default
        self._active_panel = "chart"
        self._analysis_result: Optional[Dict[str, Any]] = None

        self._root = tk.Tk()
        self._setup_root()
        self._apply_theme()
        self._build_ui()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_root(self) -> None:
        self._root.title("CryptVault  |  Professional Crypto Analysis")
        self._root.geometry("1440x860")
        self._root.minsize(1100, 700)
        self._root.configure(bg=BG_DEEP)

        try:
            self._root.tk.call("tk", "scaling", 1.25)
        except Exception:
            pass

        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_theme(self) -> None:
        style = ttk.Style(self._root)
        apply_ttk_theme(style)

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_topbar()
        content = ttk.Frame(self._root, style="TFrame")
        content.pack(fill="both", expand=True)
        self._build_sidebar(content)
        self._build_main(content)
        self._build_statusbar()
        self._show_panel("chart", force=True)

    def _build_topbar(self) -> None:
        bar = tk.Frame(self._root, bg=BG_DEEP, height=TOPBAR_HEIGHT)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Logo
        tk.Label(bar, text="CryptVault", bg=BG_DEEP, fg=ACCENT_BLUE,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        tk.Label(bar, text="v6.0", bg=BG_DEEP, fg=TEXT_MUTED,
                 font=FONT_TINY).pack(side="left")

        # Symbol search
        tk.Frame(bar, bg=BG_DEEP, width=30).pack(side="left")
        tk.Label(bar, text="Symbol:", bg=BG_DEEP, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(side="left", padx=(0, 4))
        self._sym_var = tk.StringVar(value="BTC-USD")
        sym_entry = tk.Entry(
            bar, textvariable=self._sym_var,
            bg=BG_HOVER, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            font=FONT_BODY, relief="flat", bd=0, width=14,
        )
        sym_entry.pack(side="left", ipady=5, padx=(0, 4))
        sym_entry.bind("<Return>", lambda e: self._run_analysis())

        ttk.Button(bar, text="Analyze", command=self._run_analysis,
                   style="Accent.TButton").pack(side="left", padx=4)

        # Popular assets quick-pick
        tk.Frame(bar, bg=BG_BORDER, width=1).pack(side="left", fill="y", padx=12, pady=10)
        for sym in ["BTC", "ETH", "SOL", "BNB", "XRP"]:
            btn = tk.Button(
                bar, text=sym, bg=BG_DEEP, fg=TEXT_SECONDARY,
                activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
                relief="flat", font=FONT_SMALL, cursor="hand2", bd=0,
                command=lambda s=sym: self._quick_load(s),
            )
            btn.pack(side="left", padx=2, ipady=4, ipadx=6)

        # Timeframe buttons (right side)
        tk.Frame(bar, bg=BG_BORDER, width=1).pack(side="right", fill="y", padx=12, pady=10)
        self._tf_btns: List[tk.Button] = []
        for i, (label, period, interval) in enumerate(reversed(TIMEFRAMES)):
            idx = len(TIMEFRAMES) - 1 - i
            btn = tk.Button(
                bar, text=label,
                bg=BG_PANEL if idx == self._current_tf_idx else BG_DEEP,
                fg=ACCENT_BLUE if idx == self._current_tf_idx else TEXT_SECONDARY,
                activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
                relief="flat", font=FONT_SMALL, cursor="hand2", bd=0,
                command=lambda ix=idx: self._set_timeframe(ix),
            )
            btn.pack(side="right", padx=2, ipady=4, ipadx=8)
            self._tf_btns.append(btn)
        self._tf_btns.reverse()

        # Loading indicator
        self._lbl_loading = tk.Label(bar, text="", bg=BG_DEEP, fg=YELLOW, font=FONT_SMALL)
        self._lbl_loading.pack(side="right", padx=10)

    def _build_sidebar(self, parent: ttk.Frame) -> None:
        sidebar = tk.Frame(parent, bg=BG_DEEP, width=SIDEBAR_WIDTH)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="NAVIGATE", bg=BG_DEEP, fg=TEXT_MUTED,
                 font=FONT_TINY).pack(anchor="w", padx=14, pady=(16, 4))

        self._nav_btns: Dict[str, tk.Button] = {}
        for label, key in NAV_ITEMS:
            btn = tk.Button(
                sidebar, text=label, anchor="w",
                bg=BG_DEEP, fg=TEXT_SECONDARY,
                activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
                relief="flat", font=FONT_BODY, cursor="hand2", bd=0,
                command=lambda k=key: self._show_panel(k),
            )
            btn.pack(fill="x", padx=8, pady=1, ipady=8, ipadx=10)
            self._nav_btns[key] = btn

        tk.Frame(sidebar, bg=BG_BORDER, height=1).pack(fill="x", padx=14, pady=12)

        tk.Label(sidebar, text="LAST ANALYSIS", bg=BG_DEEP, fg=TEXT_MUTED,
                 font=FONT_TINY).pack(anchor="w", padx=14, pady=(0, 4))

        self._stat_labels: Dict[str, tk.Label] = {}
        for key in ("Symbol", "Price", "Change", "Patterns", "Signal"):
            row = tk.Frame(sidebar, bg=BG_DEEP)
            row.pack(fill="x", padx=14, pady=1)
            tk.Label(row, text=f"{key}:", bg=BG_DEEP, fg=TEXT_MUTED, font=FONT_TINY).pack(side="left")
            lbl = tk.Label(row, text="—", bg=BG_DEEP, fg=TEXT_SECONDARY, font=FONT_TINY)
            lbl.pack(side="right")
            self._stat_labels[key] = lbl

        tk.Frame(sidebar, bg=BG_DEEP).pack(fill="both", expand=True)
        tk.Label(sidebar, text="Made by\nMeridianAlgo", bg=BG_DEEP, fg=TEXT_MUTED,
                 font=FONT_TINY).pack(side="bottom", pady=10)

    def _build_main(self, parent: ttk.Frame) -> None:
        self._main_frame = ttk.Frame(parent, style="TFrame")
        self._main_frame.pack(side="left", fill="both", expand=True)

        paned = ttk.PanedWindow(self._main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        self._chart_panel = ChartPanel(paned)
        paned.add(self._chart_panel, weight=3)

        self._analysis_panel = AnalysisPanel(paned)
        paned.add(self._analysis_panel, weight=1)

    def _build_statusbar(self) -> None:
        bar = tk.Frame(self._root, bg=BG_DEEP, height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_lbl = tk.Label(bar, text="Ready", bg=BG_DEEP, fg=TEXT_MUTED, font=FONT_TINY)
        self._status_lbl.pack(side="left", padx=10)

        tk.Label(bar, text="CryptVault v6.0  |  MeridianAlgo",
                 bg=BG_DEEP, fg=TEXT_MUTED, font=FONT_TINY).pack(side="right", padx=10)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _show_panel(self, key: str, force: bool = False) -> None:
        if key == self._active_panel and not force:
            return
        self._active_panel = key

        for k, btn in self._nav_btns.items():
            btn.config(
                bg=BG_PANEL if k == key else BG_DEEP,
                fg=ACCENT_BLUE if k == key else TEXT_SECONDARY,
            )

    # ------------------------------------------------------------------
    # Timeframe
    # ------------------------------------------------------------------

    def _set_timeframe(self, idx: int) -> None:
        self._current_tf_idx = idx
        for i, btn in enumerate(self._tf_btns):
            btn.config(
                bg=BG_PANEL if i == idx else BG_DEEP,
                fg=ACCENT_BLUE if i == idx else TEXT_SECONDARY,
            )
        if hasattr(self, "_last_analyzed_symbol"):
            self._run_analysis()

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def _quick_load(self, sym: str) -> None:
        self._sym_var.set(sym + "-USD")
        self._run_analysis()

    def _run_analysis(self) -> None:
        symbol = self._sym_var.get().strip().upper()
        if not symbol:
            return

        self._current_symbol = symbol
        self._lbl_loading.config(text="Analyzing...")
        self._set_status(f"Fetching {symbol}...")

        t = threading.Thread(target=self._analysis_thread, args=(symbol,), daemon=True)
        t.start()

    def _analysis_thread(self, symbol: str) -> None:
        try:
            label, period, interval = TIMEFRAMES[self._current_tf_idx]

            import yfinance as yf

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df is None or df.empty:
                self._root.after(0, lambda: self._on_analysis_error(f"No data for {symbol}"))
                return

            df.columns = [c.lower() for c in df.columns]
            df = df.dropna(subset=["close"])

            patterns = self._detect_patterns(df)
            prediction = self._run_prediction(df)

            self._root.after(0, lambda: self._on_analysis_done(symbol, df, patterns, prediction))

        except Exception as e:
            logger.error("Analysis error: %s", e, exc_info=True)
            self._root.after(0, lambda: self._on_analysis_error(str(e)))

    def _detect_patterns(self, df) -> List[Dict[str, Any]]:
        """Run comprehensive pattern detection."""
        try:
            from ..patterns.comprehensive import ComprehensivePatternDetector
            detector = ComprehensivePatternDetector()
            return detector.detect_all(df)
        except Exception as e:
            logger.warning("Pattern detection failed: %s", e)
            return []

    def _run_prediction(self, df) -> Optional[Dict[str, Any]]:
        """Run ML prediction with momentum fallback."""
        try:
            from ..ml.production_predictor import ProductionPredictor
            predictor = ProductionPredictor()
            result = predictor.predict(df)
            if result and isinstance(result, dict):
                return result
        except Exception as e:
            logger.debug("Production predictor failed: %s", e)

        # Momentum fallback
        closes = df["close"].values
        if len(closes) < 5:
            return None

        recent = closes[-5:]
        momentum = (recent[-1] - recent[0]) / recent[0]
        pred_price = closes[-1] * (1 + momentum * 0.3)
        direction = "UP" if momentum > 0.001 else ("DOWN" if momentum < -0.001 else "NEUTRAL")

        return {
            "predicted_price": pred_price,
            "direction": direction,
            "confidence": min(0.95, abs(momentum) * 10 + 0.5),
            "horizon": TIMEFRAMES[self._current_tf_idx][0],
            "model": "Momentum",
        }

    def _on_analysis_done(self, symbol: str, df, patterns: List, prediction: Optional[Dict]) -> None:
        self._last_analyzed_symbol = symbol
        self._lbl_loading.config(text="")
        self._set_status(f"Done  |  {symbol}  |  {len(patterns)} patterns  |  {len(df)} bars")

        self._chart_panel.update_chart(df, patterns, symbol=symbol)
        self._analysis_panel.update(prediction=prediction, patterns=patterns)

        closes = df["close"].values
        if len(closes) >= 2:
            change = (closes[-1] - closes[0]) / closes[0] * 100
            sign = "+" if change >= 0 else ""
            color = GREEN if change >= 0 else RED
            self._stat_labels["Symbol"].config(text=symbol)
            self._stat_labels["Price"].config(text=f"${closes[-1]:,.2f}")
            self._stat_labels["Change"].config(text=f"{sign}{change:.1f}%", fg=color)
            self._stat_labels["Patterns"].config(text=str(len(patterns)))
            bull = sum(1 for p in patterns if p.get("bullish", False))
            bear = len(patterns) - bull
            sig = "Bullish" if bull > bear else ("Bearish" if bear > bull else "Neutral")
            sig_color = GREEN if bull > bear else (RED if bear > bull else YELLOW)
            self._stat_labels["Signal"].config(text=sig, fg=sig_color)

    def _on_analysis_error(self, msg: str) -> None:
        self._lbl_loading.config(text="")
        self._set_status(f"Error: {msg}")
        messagebox.showerror("Analysis Error", msg)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, text: str) -> None:
        self._status_lbl.config(text=text)

    def _on_close(self) -> None:
        self._root.destroy()

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        self._root.mainloop()
