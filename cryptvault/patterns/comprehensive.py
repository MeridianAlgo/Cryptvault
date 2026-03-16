"""
Comprehensive Pattern Detector
Detects 50+ chart patterns across 7 categories:
  1. Single candlestick (Doji, Hammer, Shooting Star, Spinning Top, Marubozu…)
  2. Two-candle (Engulfing, Harami, Piercing, Dark Cloud Cover, Tweezer…)
  3. Three-candle (Morning/Evening Star, Three Soldiers/Crows, Abandoned Baby…)
  4. Reversal chart patterns (Head & Shoulders, Double/Triple Top/Bottom)
  5. Continuation patterns (Triangles, Wedges, Flags, Pennants, Cup & Handle)
  6. Harmonic patterns (Gartley, Butterfly, Bat, Crab, Shark, Cypher)
  7. Divergence patterns (RSI, MACD)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Result type
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Pattern:
    name: str
    category: str          # candlestick|reversal|continuation|harmonic|divergence
    bullish: bool
    strength: float        # 0.0 – 1.0
    index: int             # bar index where pattern completes
    description: str = ""
    target: Optional[float] = None
    stop_loss: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "name": self.name,
            "category": self.category,
            "bullish": self.bullish,
            "direction": "bullish" if self.bullish else "bearish",
            "strength": self.strength,
            "index": self.index,
            "description": self.description,
            "target": self.target,
            "stop_loss": self.stop_loss,
        }
        if self.extra:
            d["extra"] = self.extra
        return d


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _body(o: float, c: float) -> float:
    return abs(c - o)

def _range(h: float, l: float) -> float:
    return h - l if h > l else 1e-9

def _upper_wick(o: float, h: float, c: float) -> float:
    return h - max(o, c)

def _lower_wick(o: float, l: float, c: float) -> float:
    return min(o, c) - l

def _is_bullish(o: float, c: float) -> bool:
    return c > o

def _atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> np.ndarray:
    n = len(closes)
    tr = np.zeros(n)
    tr[0] = highs[0] - lows[0]
    for i in range(1, n):
        tr[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
    atr = np.zeros(n)
    atr[period-1] = tr[:period].mean()
    for i in range(period, n):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    return atr

def _rsi(closes: np.ndarray, period: int = 14) -> np.ndarray:
    n = len(closes)
    deltas = np.diff(closes)
    gains  = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_g = np.full(n, np.nan)
    avg_l = np.full(n, np.nan)
    avg_g[period] = gains[:period].mean()
    avg_l[period] = losses[:period].mean()
    for i in range(period + 1, n):
        avg_g[i] = (avg_g[i-1] * (period-1) + gains[i-1]) / period
        avg_l[i] = (avg_l[i-1] * (period-1) + losses[i-1]) / period
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = np.where(avg_l != 0, avg_g / avg_l, 100)
        rsi = 100 - 100 / (1 + rs)
    return rsi

def _macd(closes: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray]:
    def ema(arr, p):
        result = np.full(len(arr), np.nan)
        result[p-1] = arr[:p].mean()
        k = 2 / (p + 1)
        for i in range(p, len(arr)):
            result[i] = arr[i] * k + result[i-1] * (1 - k)
        return result
    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(np.where(np.isnan(macd_line), 0, macd_line), signal)
    return macd_line, signal_line

def _local_extrema(values: np.ndarray, order: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    peaks  = argrelextrema(values, np.greater, order=order)[0]
    troughs = argrelextrema(values, np.less,    order=order)[0]
    return peaks, troughs


# ─────────────────────────────────────────────────────────────────────────────
# Category detectors
# ─────────────────────────────────────────────────────────────────────────────

class _CandlestickDetector:
    """Single, double, and triple candlestick pattern detection."""

    DOJI_RATIO    = 0.05
    LONG_RATIO    = 0.65
    HAMMER_LOWER  = 2.0     # lower wick >= 2× body
    HAMMER_UPPER  = 0.3     # upper wick <= 30% of range

    def detect(self, opens, highs, lows, closes, atr) -> List[Pattern]:
        patterns: List[Pattern] = []
        n = len(closes)
        for i in range(2, n):
            o, h, l, c = opens[i], highs[i], lows[i], closes[i]
            rng   = _range(h, l)
            body  = _body(o, c)
            upper = _upper_wick(o, h, c)
            lower = _lower_wick(o, l, c)
            a     = atr[i] if atr[i] > 0 else rng

            # ── Single ────────────────────────────────────────────────
            # Doji
            if body / rng < self.DOJI_RATIO:
                desc = "Equal open/close – indecision"
                if upper > lower * 2:
                    patterns.append(Pattern("Gravestone Doji", "candlestick", False, 0.70, i,
                                             "Bearish doji: long upper wick, near lows"))
                elif lower > upper * 2:
                    patterns.append(Pattern("Dragonfly Doji", "candlestick", True, 0.70, i,
                                             "Bullish doji: long lower wick, near highs"))
                else:
                    patterns.append(Pattern("Doji", "candlestick", True, 0.50, i, desc))

            # Hammer / Hanging Man
            elif lower >= body * self.HAMMER_LOWER and upper <= rng * self.HAMMER_UPPER:
                context_bull = closes[i-1] < opens[i-1]  # prior candle bearish → hammer is bullish
                patterns.append(Pattern(
                    "Hammer" if context_bull else "Hanging Man",
                    "candlestick", context_bull,
                    0.65, i,
                    "Potential reversal: long lower wick",
                ))

            # Inverted Hammer / Shooting Star
            elif upper >= body * self.HAMMER_LOWER and lower <= rng * self.HAMMER_UPPER:
                context_bull = closes[i-1] < opens[i-1]
                patterns.append(Pattern(
                    "Inverted Hammer" if context_bull else "Shooting Star",
                    "candlestick", context_bull,
                    0.65, i,
                    "Potential reversal: long upper wick",
                ))

            # Marubozu
            elif body / rng > self.LONG_RATIO and upper < a * 0.1 and lower < a * 0.1:
                bullish = _is_bullish(o, c)
                patterns.append(Pattern(
                    "Bullish Marubozu" if bullish else "Bearish Marubozu",
                    "candlestick", bullish,
                    0.80, i,
                    "Strong directional move: no wicks",
                ))

            # Spinning Top
            elif body / rng < 0.35 and upper > body and lower > body:
                patterns.append(Pattern("Spinning Top", "candlestick", True, 0.40, i,
                                         "Small body with long wicks – indecision"))

            # ── Two-candle (needs i >= 1) ──────────────────────────────
            if i >= 1:
                o1, h1, l1, c1 = opens[i-1], highs[i-1], lows[i-1], closes[i-1]
                body1 = _body(o1, c1)

                # Engulfing
                if body1 > 0 and not _is_bullish(o1, c1) and _is_bullish(o, c):
                    if o < c1 and c > o1 and body > body1:
                        patterns.append(Pattern("Bullish Engulfing", "candlestick", True, 0.80, i,
                                                 "Current candle engulfs prior bearish candle"))
                elif body1 > 0 and _is_bullish(o1, c1) and not _is_bullish(o, c):
                    if o > c1 and c < o1 and body > body1:
                        patterns.append(Pattern("Bearish Engulfing", "candlestick", False, 0.80, i,
                                                 "Current candle engulfs prior bullish candle"))

                # Harami
                if body1 > 0 and _is_bullish(o1, c1) and not _is_bullish(o, c):
                    if o < c1 and c > o1:
                        patterns.append(Pattern("Bearish Harami", "candlestick", False, 0.55, i,
                                                 "Small bearish inside prior bullish – potential reversal"))
                elif body1 > 0 and not _is_bullish(o1, c1) and _is_bullish(o, c):
                    if o > c1 and c < o1:
                        patterns.append(Pattern("Bullish Harami", "candlestick", True, 0.55, i,
                                                 "Small bullish inside prior bearish – potential reversal"))

                # Piercing / Dark Cloud Cover
                if not _is_bullish(o1, c1) and _is_bullish(o, c):
                    mid1 = (o1 + c1) / 2
                    if o < l1 and c > mid1 and c < o1:
                        patterns.append(Pattern("Piercing Line", "candlestick", True, 0.72, i,
                                                 "Bullish reversal: close above prior midpoint"))

                if _is_bullish(o1, c1) and not _is_bullish(o, c):
                    mid1 = (o1 + c1) / 2
                    if o > h1 and c < mid1 and c > o1:
                        patterns.append(Pattern("Dark Cloud Cover", "candlestick", False, 0.72, i,
                                                 "Bearish reversal: close below prior midpoint"))

                # Tweezer Top / Bottom
                if abs(h - h1) / (a + 1e-9) < 0.05 and not _is_bullish(o, c):
                    patterns.append(Pattern("Tweezer Top", "candlestick", False, 0.60, i,
                                             "Equal highs – resistance level"))
                if abs(l - l1) / (a + 1e-9) < 0.05 and _is_bullish(o, c):
                    patterns.append(Pattern("Tweezer Bottom", "candlestick", True, 0.60, i,
                                             "Equal lows – support level"))

            # ── Three-candle (needs i >= 2) ────────────────────────────
            if i >= 2:
                o2, h2, l2, c2 = opens[i-2], highs[i-2], lows[i-2], closes[i-2]
                o1, h1, l1, c1 = opens[i-1], highs[i-1], lows[i-1], closes[i-1]

                # Morning Star (bear→small→bull)
                if (not _is_bullish(o2, c2) and _body(o2, c2) > a * 0.6
                        and _body(o1, c1) < a * 0.3
                        and _is_bullish(o, c) and _body(o, c) > a * 0.6
                        and c > (o2 + c2) / 2):
                    patterns.append(Pattern("Morning Star", "candlestick", True, 0.88, i,
                                             "Strong bullish reversal: bear→star→bull"))

                # Evening Star
                if (_is_bullish(o2, c2) and _body(o2, c2) > a * 0.6
                        and _body(o1, c1) < a * 0.3
                        and not _is_bullish(o, c) and _body(o, c) > a * 0.6
                        and c < (o2 + c2) / 2):
                    patterns.append(Pattern("Evening Star", "candlestick", False, 0.88, i,
                                             "Strong bearish reversal: bull→star→bear"))

                # Three White Soldiers
                if (all(_is_bullish(opens[j], closes[j]) for j in range(i-2, i+1))
                        and closes[i-1] > closes[i-2] and closes[i] > closes[i-1]
                        and all(_body(opens[j], closes[j]) > a * 0.4 for j in range(i-2, i+1))):
                    patterns.append(Pattern("Three White Soldiers", "candlestick", True, 0.85, i,
                                             "Three consecutive strong bullish candles"))

                # Three Black Crows
                if (all(not _is_bullish(opens[j], closes[j]) for j in range(i-2, i+1))
                        and closes[i-1] < closes[i-2] and closes[i] < closes[i-1]
                        and all(_body(opens[j], closes[j]) > a * 0.4 for j in range(i-2, i+1))):
                    patterns.append(Pattern("Three Black Crows", "candlestick", False, 0.85, i,
                                             "Three consecutive strong bearish candles"))

                # Abandoned Baby (gap doji)
                doji_body = _body(o1, c1)
                gap_up   = l1 > h2 and l > h1
                gap_down = h1 < l2 and h < l1
                if gap_up and doji_body / (_range(h1, l1) + 1e-9) < 0.1 and not _is_bullish(o, c):
                    patterns.append(Pattern("Abandoned Baby Top", "candlestick", False, 0.90, i,
                                             "Gap + doji + gap: strong bearish reversal"))
                if gap_down and doji_body / (_range(h1, l1) + 1e-9) < 0.1 and _is_bullish(o, c):
                    patterns.append(Pattern("Abandoned Baby Bottom", "candlestick", True, 0.90, i,
                                             "Gap + doji + gap: strong bullish reversal"))

        return patterns


class _ChartPatternDetector:
    """Reversal and continuation chart pattern detection using pivot points."""

    def __init__(self, lookback: int = 5):
        self.lookback = lookback

    def detect(self, opens, highs, lows, closes, atr) -> List[Pattern]:
        patterns: List[Pattern] = []
        n = len(closes)
        if n < 30:
            return patterns

        peaks,  troughs = _local_extrema(closes, order=self.lookback)

        # ── Double Top ────────────────────────────────────────────────
        for i in range(1, len(peaks)):
            p1, p2 = peaks[i-1], peaks[i]
            if p2 - p1 < 5:
                continue
            if abs(closes[p1] - closes[p2]) / closes[p1] < 0.03:
                between = closes[p1:p2]
                neck = between.min()
                height = closes[p1] - neck
                if height / closes[p1] > 0.02:
                    patterns.append(Pattern(
                        "Double Top", "reversal", False, 0.80, p2,
                        "Two equal peaks – bearish reversal signal",
                        target=neck - height,
                        stop_loss=closes[p2] * 1.02,
                        extra={"p1": int(p1), "p2": int(p2), "neck": float(neck)},
                    ))

        # ── Double Bottom ─────────────────────────────────────────────
        for i in range(1, len(troughs)):
            t1, t2 = troughs[i-1], troughs[i]
            if t2 - t1 < 5:
                continue
            if abs(closes[t1] - closes[t2]) / closes[t1] < 0.03:
                between = closes[t1:t2]
                neck = between.max()
                height = neck - closes[t1]
                if height / closes[t1] > 0.02:
                    patterns.append(Pattern(
                        "Double Bottom", "reversal", True, 0.80, t2,
                        "Two equal troughs – bullish reversal signal",
                        target=neck + height,
                        stop_loss=closes[t2] * 0.98,
                        extra={"t1": int(t1), "t2": int(t2), "neck": float(neck)},
                    ))

        # ── Triple Top / Bottom ───────────────────────────────────────
        for i in range(2, len(peaks)):
            p1, p2, p3 = peaks[i-2], peaks[i-1], peaks[i]
            if p3 - p1 < 10:
                continue
            if (abs(closes[p1] - closes[p2]) / closes[p1] < 0.03
                    and abs(closes[p2] - closes[p3]) / closes[p2] < 0.03):
                patterns.append(Pattern(
                    "Triple Top", "reversal", False, 0.85, p3,
                    "Three equal peaks – strong bearish reversal",
                    extra={"p1": int(p1), "p2": int(p2), "p3": int(p3)},
                ))

        for i in range(2, len(troughs)):
            t1, t2, t3 = troughs[i-2], troughs[i-1], troughs[i]
            if t3 - t1 < 10:
                continue
            if (abs(closes[t1] - closes[t2]) / closes[t1] < 0.03
                    and abs(closes[t2] - closes[t3]) / closes[t2] < 0.03):
                patterns.append(Pattern(
                    "Triple Bottom", "reversal", True, 0.85, t3,
                    "Three equal troughs – strong bullish reversal",
                    extra={"p1": int(t1), "p2": int(t2), "p3": int(t3)},
                ))

        # ── Head & Shoulders ──────────────────────────────────────────
        for i in range(2, len(peaks)):
            ls, head, rs = peaks[i-2], peaks[i-1], peaks[i]
            if rs - ls < 10:
                continue
            if (closes[head] > closes[ls] * 1.02
                    and closes[head] > closes[rs] * 1.02
                    and abs(closes[ls] - closes[rs]) / closes[ls] < 0.05):
                neckline = min(closes[ls:rs].min(), closes[rs:min(n, rs+5)].min())
                height = closes[head] - neckline
                patterns.append(Pattern(
                    "Head & Shoulders", "reversal", False, 0.87, rs,
                    "Classic bearish reversal: LS-Head-RS",
                    target=neckline - height,
                    stop_loss=closes[head] * 1.01,
                    extra={"ls": int(ls), "head": int(head), "rs": int(rs), "neckline": float(neckline)},
                ))

        # ── Inverse Head & Shoulders ──────────────────────────────────
        for i in range(2, len(troughs)):
            ls, head, rs = troughs[i-2], troughs[i-1], troughs[i]
            if rs - ls < 10:
                continue
            if (closes[head] < closes[ls] * 0.98
                    and closes[head] < closes[rs] * 0.98
                    and abs(closes[ls] - closes[rs]) / closes[ls] < 0.05):
                neckline = max(closes[ls:rs].max(), closes[rs:min(n, rs+5)].max())
                height = neckline - closes[head]
                patterns.append(Pattern(
                    "Inverse Head & Shoulders", "reversal", True, 0.87, rs,
                    "Classic bullish reversal: LS-Head-RS",
                    target=neckline + height,
                    stop_loss=closes[head] * 0.99,
                    extra={"ls": int(ls), "head": int(head), "rs": int(rs), "neckline": float(neckline)},
                ))

        # ── Triangles ─────────────────────────────────────────────────
        if n >= 20:
            self._detect_triangles(closes, highs, lows, atr, n, patterns)

        # ── Flags / Pennants ──────────────────────────────────────────
        if n >= 15:
            self._detect_flags(closes, highs, lows, atr, n, patterns)

        # ── Cup and Handle ────────────────────────────────────────────
        if n >= 40:
            self._detect_cup_handle(closes, highs, lows, n, patterns)

        return patterns

    def _detect_triangles(self, closes, highs, lows, atr, n, patterns):
        window = min(40, n // 2)
        start_idx = n - window
        seg = closes[-window:]
        seg_h = highs[-window:]
        seg_l = lows[-window:]
        x = np.arange(len(seg))

        coef_h = np.polyfit(x, seg_h, 1)
        coef_l = np.polyfit(x, seg_l, 1)
        slope_h, slope_l = coef_h[0], coef_l[0]

        # Trendline endpoints for chart drawing
        extra_tl = {
            "start": int(start_idx),
            "high_start": float(np.polyval(coef_h, 0)),
            "high_end":   float(np.polyval(coef_h, window - 1)),
            "low_start":  float(np.polyval(coef_l, 0)),
            "low_end":    float(np.polyval(coef_l, window - 1)),
        }

        if slope_h < -atr[-1] * 0.01 and slope_l > atr[-1] * 0.01:
            patterns.append(Pattern("Symmetrical Triangle", "continuation", True, 0.65, n-1,
                                     "Converging trendlines – breakout imminent",
                                     extra=extra_tl))
        elif abs(slope_h) < atr[-1] * 0.01 and slope_l > atr[-1] * 0.01:
            patterns.append(Pattern("Ascending Triangle", "continuation", True, 0.72, n-1,
                                     "Flat resistance, rising support – bullish breakout likely",
                                     extra=extra_tl))
        elif slope_h < -atr[-1] * 0.01 and abs(slope_l) < atr[-1] * 0.01:
            patterns.append(Pattern("Descending Triangle", "continuation", False, 0.72, n-1,
                                     "Falling resistance, flat support – bearish breakout likely",
                                     extra=extra_tl))

        if slope_h > 0 and slope_l > 0 and slope_l > slope_h:
            patterns.append(Pattern("Rising Wedge", "reversal", False, 0.68, n-1,
                                     "Both trendlines rising, narrowing – bearish reversal",
                                     extra=extra_tl))
        elif slope_h < 0 and slope_l < 0 and slope_h < slope_l:
            patterns.append(Pattern("Falling Wedge", "reversal", True, 0.68, n-1,
                                     "Both trendlines falling, narrowing – bullish reversal",
                                     extra=extra_tl))

    def _detect_flags(self, closes, highs, lows, atr, n, patterns):
        lookback = min(20, n // 2)
        pole_end = n - lookback
        if pole_end < 5:
            return
        pole_move = closes[pole_end] - closes[pole_end - 5]
        if abs(pole_move) < atr[n-1] * 2:
            return   # not a strong pole

        flag = closes[pole_end:]
        if len(flag) < 5:
            return
        flag_slope = np.polyfit(np.arange(len(flag)), flag, 1)[0]
        bullish_pole = pole_move > 0

        if bullish_pole and flag_slope < 0:
            patterns.append(Pattern("Bull Flag", "continuation", True, 0.75, n-1,
                                     "Strong up-move followed by consolidation pullback"))
        elif not bullish_pole and flag_slope > 0:
            patterns.append(Pattern("Bear Flag", "continuation", False, 0.75, n-1,
                                     "Strong down-move followed by consolidation bounce"))

        # Pennant: flag with narrowing price range
        flag_range = np.max(flag) - np.min(flag)
        pole_range = np.max(closes[pole_end-5:pole_end]) - np.min(closes[pole_end-5:pole_end])
        if flag_range < pole_range * 0.4:
            tag = "Bull Pennant" if bullish_pole else "Bear Pennant"
            patterns.append(Pattern(tag, "continuation", bullish_pole, 0.72, n-1,
                                     "Tight consolidation after strong move – trend continuation"))

    def _detect_cup_handle(self, closes, highs, lows, n, patterns):
        window = min(60, n)
        seg = closes[-window:]
        left_rim  = seg[:5].mean()
        bottom    = seg[window//3: 2*window//3].min()
        right_rim = seg[-10:].max()

        cup_depth = left_rim - bottom
        if cup_depth / left_rim < 0.1:
            return
        if abs(left_rim - right_rim) / left_rim < 0.05:
            handle_low = seg[-5:].min()
            if handle_low > bottom and handle_low < right_rim * 0.97:
                patterns.append(Pattern("Cup & Handle", "continuation", True, 0.82, n-1,
                                         "U-shaped base with small handle – bullish breakout setup"))


class _HarmonicDetector:
    """Detect harmonic patterns: Gartley, Butterfly, Bat, Crab, Shark, Cypher."""

    PATTERNS = {
        "Gartley":   {"XB": (0.618, 0.618), "AC": (0.382, 0.886), "BD": (1.272, 1.618)},
        "Butterfly": {"XB": (0.786, 0.786), "AC": (0.382, 0.886), "BD": (1.618, 2.618)},
        "Bat":       {"XB": (0.382, 0.500), "AC": (0.382, 0.886), "BD": (1.618, 2.618)},
        "Crab":      {"XB": (0.382, 0.618), "AC": (0.382, 0.886), "BD": (2.240, 3.618)},
        "Shark":     {"XB": (0.446, 0.618), "AC": (1.130, 1.618), "BD": (0.886, 1.130)},
        "Cypher":    {"XB": (0.382, 0.618), "AC": (1.130, 1.414), "BD": (0.786, 0.786)},
    }

    TOLERANCE = 0.08

    def detect(self, opens, highs, lows, closes, atr) -> List[Pattern]:
        patterns: List[Pattern] = []
        n = len(closes)
        if n < 20:
            return patterns

        peaks, troughs = _local_extrema(closes, order=3)
        all_pivots = sorted(
            [(i, closes[i], "peak") for i in peaks] +
            [(i, closes[i], "trough") for i in troughs],
            key=lambda x: x[0],
        )

        if len(all_pivots) < 5:
            return patterns

        for i in range(len(all_pivots) - 4):
            X, A, B, C, D_pivot = all_pivots[i:i+5]
            xi, xa_price = X[0], X[1]
            ai, aa_price = A[0], A[1]
            bi, ab_price = B[0], B[1]
            ci, ac_price = C[0], C[1]
            di, ad_price = D_pivot[0], D_pivot[1]

            xa = abs(aa_price - xa_price)
            if xa < 1e-9:
                continue
            ab = abs(ab_price - aa_price)
            bc = abs(ac_price - ab_price)
            cd = abs(ad_price - ac_price)

            xb_ratio = ab / xa
            ac_ratio = bc / ab if ab > 0 else 0
            bd_ratio = cd / (ab if ab > 0 else 1)

            bullish = aa_price > xa_price   # X-A up → A-B down → bullish completion

            for name, ratios in self.PATTERNS.items():
                xb_lo, xb_hi = ratios["XB"]
                ac_lo, ac_hi = ratios["AC"]
                bd_lo, bd_hi = ratios["BD"]

                tol = self.TOLERANCE
                if (xb_lo - tol <= xb_ratio <= xb_hi + tol
                        and ac_lo - tol <= ac_ratio <= ac_hi + tol
                        and bd_lo - tol <= bd_ratio <= bd_hi + tol):
                    strength = 1.0 - (abs(xb_ratio - (xb_lo + xb_hi) / 2) +
                                      abs(ac_ratio - (ac_lo + ac_hi) / 2) +
                                      abs(bd_ratio - (bd_lo + bd_hi) / 2)) / 3

                    patterns.append(Pattern(
                        f"{name} ({'Bullish' if bullish else 'Bearish'})",
                        "harmonic", bullish,
                        min(0.95, max(0.50, strength)),
                        di,
                        f"Harmonic {name} pattern at PRZ",
                    ))

        return patterns


class _DivergenceDetector:
    """Detect RSI and MACD divergence patterns."""

    def detect(self, opens, highs, lows, closes, atr) -> List[Pattern]:
        patterns: List[Pattern] = []
        n = len(closes)
        if n < 30:
            return patterns

        rsi  = _rsi(closes)
        macd_line, signal_line = _macd(closes)

        peaks,   troughs   = _local_extrema(closes, order=5)
        r_peaks, r_troughs = _local_extrema(np.where(np.isnan(rsi), 50, rsi), order=5)

        # ── RSI Bearish Divergence (higher price highs, lower RSI highs) ──
        for i in range(1, min(len(peaks), len(r_peaks))):
            cp1, cp2 = peaks[i-1], peaks[i]
            rp1, rp2 = r_peaks[i-1], r_peaks[i]
            if cp2 - cp1 < 5 or rp2 - rp1 < 5:
                continue
            if closes[cp2] > closes[cp1] and rsi[rp2] < rsi[rp1]:
                patterns.append(Pattern(
                    "RSI Bearish Divergence", "divergence", False, 0.75, cp2,
                    "Price making higher highs while RSI making lower highs",
                ))

        # ── RSI Bullish Divergence (lower price lows, higher RSI lows) ───
        for i in range(1, min(len(troughs), len(r_troughs))):
            ct1, ct2 = troughs[i-1], troughs[i]
            rt1, rt2 = r_troughs[i-1], r_troughs[i]
            if ct2 - ct1 < 5 or rt2 - rt1 < 5:
                continue
            if closes[ct2] < closes[ct1] and rsi[rt2] > rsi[rt1]:
                patterns.append(Pattern(
                    "RSI Bullish Divergence", "divergence", True, 0.75, ct2,
                    "Price making lower lows while RSI making higher lows",
                ))

        # ── MACD Divergence ───────────────────────────────────────────
        valid = ~np.isnan(macd_line)
        if valid.sum() < 20:
            return patterns

        m_peaks,  m_troughs = _local_extrema(np.where(np.isnan(macd_line), 0, macd_line), order=5)

        for i in range(1, min(len(peaks), len(m_peaks))):
            cp1, cp2 = peaks[i-1], peaks[i]
            mp1, mp2 = m_peaks[i-1], m_peaks[i]
            if cp2 - cp1 < 5 or mp2 - mp1 < 5:
                continue
            if closes[cp2] > closes[cp1] and macd_line[mp2] < macd_line[mp1]:
                patterns.append(Pattern(
                    "MACD Bearish Divergence", "divergence", False, 0.70, cp2,
                    "Price making higher highs while MACD making lower highs",
                ))

        for i in range(1, min(len(troughs), len(m_troughs))):
            ct1, ct2 = troughs[i-1], troughs[i]
            mt1, mt2 = m_troughs[i-1], m_troughs[i]
            if ct2 - ct1 < 5 or mt2 - mt1 < 5:
                continue
            if closes[ct2] < closes[ct1] and macd_line[mt2] > macd_line[mt1]:
                patterns.append(Pattern(
                    "MACD Bullish Divergence", "divergence", True, 0.70, ct2,
                    "Price making lower lows while MACD making higher lows",
                ))

        return patterns


# ─────────────────────────────────────────────────────────────────────────────
# Main detector
# ─────────────────────────────────────────────────────────────────────────────

class ComprehensivePatternDetector:
    """
    Runs all pattern detectors and returns a unified list.

    Input: pandas DataFrame with columns [open, high, low, close, volume]
    Output: List[dict]  (each dict has name, category, bullish, strength, index, description…)
    """

    def __init__(self):
        self._cs    = _CandlestickDetector()
        self._chart = _ChartPatternDetector()
        self._harm  = _HarmonicDetector()
        self._div   = _DivergenceDetector()

    def detect_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect all patterns. Returns list of dicts."""
        if df is None or df.empty or len(df) < 5:
            return []

        df = df.copy()
        df.columns = [c.lower() for c in df.columns]

        opens  = df["open"].values  if "open"   in df.columns else df["close"].values
        highs  = df["high"].values  if "high"   in df.columns else df["close"].values
        lows   = df["low"].values   if "low"    in df.columns else df["close"].values
        closes = df["close"].values
        vols   = df["volume"].values if "volume" in df.columns else np.zeros(len(closes))

        atr = _atr(highs, lows, closes)

        all_patterns: List[Pattern] = []

        for detector_name, detector_fn in [
            ("candlestick", lambda: self._cs.detect(opens, highs, lows, closes, atr)),
            ("chart",       lambda: self._chart.detect(opens, highs, lows, closes, atr)),
            ("harmonic",    lambda: self._harm.detect(opens, highs, lows, closes, atr)),
            ("divergence",  lambda: self._div.detect(opens, highs, lows, closes, atr)),
        ]:
            try:
                results = detector_fn()
                all_patterns.extend(results)
            except Exception as e:
                logger.debug("Pattern detector '%s' error: %s", detector_name, e)

        # De-duplicate by (name, index) and sort by recency then strength
        # Ensure all indices are ints
        for p in all_patterns:
            if not isinstance(p.index, int):
                p.index = int(p.index) if str(p.index).isdigit() else len(closes) - 1

        seen = set()
        unique: List[Pattern] = []
        for p in sorted(all_patterns, key=lambda x: (-x.index, -x.strength)):
            key = (p.name, p.index)
            if key not in seen:
                seen.add(key)
                unique.append(p)

        return [p.to_dict() for p in unique[:50]]

    def detect_realtime(self, df: pd.DataFrame, last_n: int = 10) -> List[Dict[str, Any]]:
        """Fast detection on last N bars only (for real-time use)."""
        if df is None or len(df) < 5:
            return []
        # Run on full df but only return patterns in last N bars
        all_pats = self.detect_all(df)
        n = len(df)
        return [p for p in all_pats if p.get("index", 0) >= n - last_n]
