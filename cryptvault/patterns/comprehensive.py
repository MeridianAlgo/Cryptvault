"""
Comprehensive Pattern Detector
Detects 70+ chart patterns across 8 categories:
  1. Single candlestick (Doji, Hammer, Shooting Star, Spinning Top, Marubozu…)
  2. Two-candle (Engulfing, Harami, Piercing, Dark Cloud Cover, Tweezer, Kicker…)
  3. Three-candle (Morning/Evening Star, Three Soldiers/Crows, Three Inside/Outside…)
  4. Reversal chart patterns (Head & Shoulders, Double/Triple Top/Bottom, Diamond,
     Rounding Top/Bottom, Broadening, Island Reversal, Three Drives)
  5. Continuation patterns (Triangles, Wedges, Flags, Pennants, Rectangle, Cup & Handle)
  6. Harmonic patterns (Gartley, Butterfly, Bat, Crab, Shark, Cypher)
  7. Divergence patterns (RSI, MACD)
  8. Forming patterns — structures that are *incomplete* at the right edge, with the
     missing pivots projected forward so the chart can draw what would complete them

Every pattern reports the bar it completes at, plus an ``extra`` payload of pivot
indices and levels. That payload is what :mod:`cryptvault.desktop.shapes` turns
into chart geometry, so a pattern without ``extra`` can be listed but not drawn
precisely — detectors should always fill it in.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

logger = logging.getLogger(__name__)

MAX_RESULTS = 60        # patterns returned per analysis, strongest and newest first
MAX_PER_NAME = 3        # instances of any one pattern name, most recent kept


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
        # Detectors compare numpy scalars, so coerce to plain Python types —
        # np.bool_/np.float64 are not JSON-serializable.
        d: Dict[str, Any] = {
            "name": self.name,
            "category": self.category,
            "bullish": bool(self.bullish),
            "direction": "bullish" if self.bullish else "bearish",
            "strength": float(self.strength),
            "index": int(self.index),
            "description": self.description,
            "target": None if self.target is None else float(self.target),
            "stop_loss": None if self.stop_loss is None else float(self.stop_loss),
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

# How many bars each candlestick pattern occupies, counting back from the bar it
# completes at. The chart brackets exactly these candles when you select the
# pattern — a Morning Star highlighted as one candle is a lie about the setup.
_SPAN: Dict[str, int] = {
    "Morning Star": 3, "Evening Star": 3,
    "Three White Soldiers": 3, "Three Black Crows": 3,
    "Abandoned Baby Top": 3, "Abandoned Baby Bottom": 3,
    "Three Inside Up": 3, "Three Inside Down": 3,
    "Three Outside Up": 3, "Three Outside Down": 3,
    "Tri-Star Top": 3, "Tri-Star Bottom": 3,
    "Rising Three Methods": 5, "Falling Three Methods": 5,
    "Bullish Engulfing": 2, "Bearish Engulfing": 2,
    "Bullish Harami": 2, "Bearish Harami": 2,
    "Piercing Line": 2, "Dark Cloud Cover": 2,
    "Tweezer Top": 2, "Tweezer Bottom": 2,
    "Bullish Kicker": 2, "Bearish Kicker": 2,
}


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

                # Kicker — a gap straight through the prior body, no overlap at
                # all. Rare, and the strongest two-bar signal there is.
                if not _is_bullish(o1, c1) and _is_bullish(o, c) and o > o1 and l > h1:
                    patterns.append(Pattern("Bullish Kicker", "candlestick", True, 0.86, i,
                                             "Gap above the prior bearish body – violent reversal"))
                if _is_bullish(o1, c1) and not _is_bullish(o, c) and o < o1 and h < l1:
                    patterns.append(Pattern("Bearish Kicker", "candlestick", False, 0.86, i,
                                             "Gap below the prior bullish body – violent reversal"))

                # Belt Hold — opens at the extreme and runs the whole way.
                if body > a * 0.8:
                    if _is_bullish(o, c) and lower < rng * 0.05:
                        patterns.append(Pattern("Bullish Belt Hold", "candlestick", True, 0.62, i,
                                                 "Opens on the low and closes near the high"))
                    elif not _is_bullish(o, c) and upper < rng * 0.05:
                        patterns.append(Pattern("Bearish Belt Hold", "candlestick", False, 0.62, i,
                                                 "Opens on the high and closes near the low"))

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

                # Three Inside — a harami that gets confirmed by the third bar.
                body2 = _body(o2, c2)
                inside = max(o1, c1) <= max(o2, c2) and min(o1, c1) >= min(o2, c2)
                if body2 > a * 0.6 and inside:
                    if not _is_bullish(o2, c2) and _is_bullish(o1, c1) and _is_bullish(o, c) and c > o2:
                        patterns.append(Pattern("Three Inside Up", "candlestick", True, 0.78, i,
                                                 "Harami confirmed by a close above the first body"))
                    elif _is_bullish(o2, c2) and not _is_bullish(o1, c1) and not _is_bullish(o, c) and c < o2:
                        patterns.append(Pattern("Three Inside Down", "candlestick", False, 0.78, i,
                                                 "Harami confirmed by a close below the first body"))

                # Three Outside — an engulfing that gets confirmed.
                engulf_up = (not _is_bullish(o2, c2) and _is_bullish(o1, c1)
                             and o1 < c2 and c1 > o2)
                engulf_dw = (_is_bullish(o2, c2) and not _is_bullish(o1, c1)
                             and o1 > c2 and c1 < o2)
                if engulf_up and _is_bullish(o, c) and c > c1:
                    patterns.append(Pattern("Three Outside Up", "candlestick", True, 0.82, i,
                                             "Bullish engulfing extended by a third rising close"))
                if engulf_dw and not _is_bullish(o, c) and c < c1:
                    patterns.append(Pattern("Three Outside Down", "candlestick", False, 0.82, i,
                                             "Bearish engulfing extended by a third falling close"))

                # Tri-Star — three dojis in a row at an extreme.
                if all(_body(opens[j], closes[j]) / (_range(highs[j], lows[j]) + 1e-9) < self.DOJI_RATIO
                       for j in (i - 2, i - 1, i)):
                    up_trend = closes[i - 2] > closes[max(0, i - 8)]
                    patterns.append(Pattern(
                        "Tri-Star Top" if up_trend else "Tri-Star Bottom",
                        "candlestick", not up_trend, 0.80, i,
                        "Three consecutive dojis – exhaustion",
                    ))

            # ── Five-candle: Rising / Falling Three Methods ────────────
            if i >= 4:
                first, last = i - 4, i
                fo, fc = opens[first], closes[first]
                fh, fl = highs[first], lows[first]
                mids_ = range(first + 1, last)
                inside_all = all(highs[j] <= fh and lows[j] >= fl for j in mids_)
                if inside_all and _body(fo, fc) > a * 0.7 and _body(o, c) > a * 0.7:
                    if (_is_bullish(fo, fc) and _is_bullish(o, c) and c > fc
                            and all(not _is_bullish(opens[j], closes[j]) for j in mids_)):
                        patterns.append(Pattern("Rising Three Methods", "candlestick", True, 0.80, i,
                                                 "Three-bar rest inside a bull bar, then a new high close"))
                    elif (not _is_bullish(fo, fc) and not _is_bullish(o, c) and c < fc
                            and all(_is_bullish(opens[j], closes[j]) for j in mids_)):
                        patterns.append(Pattern("Falling Three Methods", "candlestick", False, 0.80, i,
                                                 "Three-bar rest inside a bear bar, then a new low close"))

        # The chart brackets `span` candles ending at `index`; without it every
        # multi-bar pattern would be highlighted as a single candle.
        for p in patterns:
            p.extra.setdefault("span", _SPAN.get(p.name, 1))

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

        # ── Rectangle / range ─────────────────────────────────────────
        if n >= 25:
            self._detect_rectangle(closes, highs, lows, atr, n, patterns)

        # ── Rounding top / bottom ─────────────────────────────────────
        if n >= 40:
            self._detect_rounding(closes, n, patterns)

        # ── Broadening formation ──────────────────────────────────────
        if n >= 30:
            self._detect_broadening(highs, lows, atr, n, patterns)

        # ── Diamond ───────────────────────────────────────────────────
        if n >= 40:
            self._detect_diamond(highs, lows, atr, n, patterns)

        # ── Three drives ──────────────────────────────────────────────
        self._detect_three_drives(closes, peaks, troughs, patterns)

        # ── Island reversal ───────────────────────────────────────────
        if n >= 12:
            self._detect_island(highs, lows, closes, n, patterns)

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

        # Channel around the consolidation, for chart drawing.
        fx = np.arange(len(flag))
        c_hi = np.polyfit(fx, highs[pole_end:], 1)
        c_lo = np.polyfit(fx, lows[pole_end:], 1)
        extra_flag = {
            "pole_start": int(pole_end - 5),
            "pole_end": int(pole_end),
            "start": int(pole_end),
            "end": int(n - 1),
            "high_start": float(np.polyval(c_hi, 0)),
            "high_end": float(np.polyval(c_hi, len(flag) - 1)),
            "low_start": float(np.polyval(c_lo, 0)),
            "low_end": float(np.polyval(c_lo, len(flag) - 1)),
        }

        if bullish_pole and flag_slope < 0:
            patterns.append(Pattern("Bull Flag", "continuation", True, 0.75, n-1,
                                     "Strong up-move followed by consolidation pullback",
                                     extra=extra_flag))
        elif not bullish_pole and flag_slope > 0:
            patterns.append(Pattern("Bear Flag", "continuation", False, 0.75, n-1,
                                     "Strong down-move followed by consolidation bounce",
                                     extra=extra_flag))

        # Pennant: flag with narrowing price range
        flag_range = np.max(flag) - np.min(flag)
        pole_range = np.max(closes[pole_end-5:pole_end]) - np.min(closes[pole_end-5:pole_end])
        if flag_range < pole_range * 0.4:
            tag = "Bull Pennant" if bullish_pole else "Bear Pennant"
            patterns.append(Pattern(tag, "continuation", bullish_pole, 0.72, n-1,
                                     "Tight consolidation after strong move – trend continuation",
                                     extra=extra_flag))

    def _detect_cup_handle(self, closes, highs, lows, n, patterns):
        window = min(60, n)
        start = n - window
        seg = closes[-window:]
        left_rim  = seg[:5].mean()
        mid = seg[window//3: 2*window//3]
        bottom    = mid.min()
        bottom_i  = start + window//3 + int(np.argmin(mid))
        right_rim = seg[-10:].max()

        cup_depth = left_rim - bottom
        if cup_depth / left_rim < 0.1:
            return
        if abs(left_rim - right_rim) / left_rim < 0.05:
            handle_low = seg[-5:].min()
            if handle_low > bottom and handle_low < right_rim * 0.97:
                patterns.append(Pattern(
                    "Cup & Handle", "continuation", True, 0.82, n-1,
                    "U-shaped base with small handle – bullish breakout setup",
                    extra={
                        "cup_start": int(start),
                        "cup_bottom": int(bottom_i),
                        "cup_end": int(n - 10),
                        "handle_start": int(n - 5),
                        "left_rim": float(left_rim),
                        "right_rim": float(right_rim),
                        "bottom": float(bottom),
                    },
                ))

    def _detect_rectangle(self, closes, highs, lows, atr, n, patterns):
        """Price boxed between a flat ceiling and a flat floor.

        A range only counts once price has been rejected from each edge at least
        twice — otherwise every quiet stretch of chart is a "rectangle".
        """
        window = min(50, n // 2)
        start = n - window
        seg_h, seg_l = highs[start:], lows[start:]
        top, bottom = float(seg_h.max()), float(seg_l.min())
        height = top - bottom
        if height <= 0 or height / closes[-1] < 0.02:
            return

        tol = height * 0.15
        touches_top = int(np.sum(seg_h >= top - tol))
        touches_bottom = int(np.sum(seg_l <= bottom + tol))
        if touches_top < 2 or touches_bottom < 2:
            return
        # The body of the move has to actually stay inside the box.
        inside = np.mean((closes[start:] < top - tol * 0.5) & (closes[start:] > bottom + tol * 0.5))
        if inside < 0.6:
            return

        bullish = closes[-1] > (top + bottom) / 2
        patterns.append(Pattern(
            "Rectangle", "continuation", bullish, 0.68, n - 1,
            f"Range held {touches_top}× at resistance and {touches_bottom}× at support",
            target=(top + height) if bullish else (bottom - height),
            stop_loss=(bottom - height * 0.1) if bullish else (top + height * 0.1),
            extra={
                "start": int(start), "end": int(n - 1),
                "top": top, "bottom": bottom,
                "touches_top": touches_top, "touches_bottom": touches_bottom,
            },
        ))

    def _detect_rounding(self, closes, n, patterns):
        """Saucer base or dome top — a quadratic that genuinely fits."""
        window = min(80, n)
        start = n - window
        seg = closes[start:]
        x = np.arange(window, dtype=float)
        coef = np.polyfit(x, seg, 2)
        fit = np.polyval(coef, x)

        var = float(np.var(seg))
        if var <= 0:
            return
        r2 = 1.0 - float(np.mean((seg - fit) ** 2)) / var
        if r2 < 0.55:
            return                                  # not actually an arc

        curve = float(coef[0])
        vertex = -coef[1] / (2 * coef[0]) if coef[0] else 0.0
        # The turn has to be inside the window, not extrapolated off the edge.
        if not (window * 0.2 < vertex < window * 0.8):
            return

        depth = abs(float(fit.max() - fit.min())) / float(seg.mean())
        if depth < 0.05:
            return

        bullish = curve > 0
        rim = float(max(fit[0], fit[-1]) if bullish else min(fit[0], fit[-1]))
        height = abs(rim - float(np.polyval(coef, vertex)))
        patterns.append(Pattern(
            "Rounding Bottom" if bullish else "Rounding Top",
            "reversal", bullish, min(0.85, 0.55 + r2 * 0.3), n - 1,
            "Gradual saucer base – accumulation" if bullish
            else "Gradual dome – distribution",
            target=(rim + height) if bullish else (rim - height),
            extra={
                "arc_start": int(start), "arc_end": int(n - 1),
                "vertex": int(start + vertex),
                "coef": [float(c) for c in coef], "fit_r2": round(r2, 3),
                "rim": rim,
            },
        ))

    @staticmethod
    def _pivots(highs, lows, start, order=3):
        """Swing highs and lows at or after ``start``.

        Broadening and diamond shapes live in the *envelope*, so they have to be
        measured from pivot to pivot. Regressing every bar averages the
        oscillation away and the formation disappears.
        """
        ph = [int(i) for i in argrelextrema(highs, np.greater, order=order)[0] if i >= start]
        tl = [int(i) for i in argrelextrema(lows, np.less, order=order)[0] if i >= start]
        return ph, tl

    @staticmethod
    def _fit_through(idxs, values):
        coef = np.polyfit(np.asarray(idxs, dtype=float), [float(values[i]) for i in idxs], 1)
        return coef

    def _detect_broadening(self, highs, lows, atr, n, patterns):
        """Megaphone — each swing high higher, each swing low lower."""
        start = n - min(60, n // 2)
        ph, tl = self._pivots(highs, lows, start)
        if len(ph) < 3 or len(tl) < 3:
            return
        ph, tl = ph[-4:], tl[-4:]
        if not all(highs[ph[k]] > highs[ph[k - 1]] for k in range(1, len(ph))):
            return
        if not all(lows[tl[k]] < lows[tl[k - 1]] for k in range(1, len(tl))):
            return

        a, b = min(ph[0], tl[0]), n - 1
        c_hi, c_lo = self._fit_through(ph, highs), self._fit_through(tl, lows)
        opening = float(np.polyval(c_hi, b) - np.polyval(c_lo, b))
        closing = float(np.polyval(c_hi, a) - np.polyval(c_lo, a))
        if closing <= 0 or opening / closing < 1.3:
            return

        patterns.append(Pattern(
            "Broadening Formation", "reversal", False, 0.64, n - 1,
            f"{len(ph)} higher highs against {len(tl)} lower lows – expanding volatility",
            extra={
                "start": int(a), "end": int(b),
                "high_start": float(np.polyval(c_hi, a)),
                "high_end": float(np.polyval(c_hi, b)),
                "low_start": float(np.polyval(c_lo, a)),
                "low_end": float(np.polyval(c_lo, b)),
                "diverging": True,
            },
        ))

    def _detect_diamond(self, highs, lows, atr, n, patterns):
        """Broadening that collapses back into converging — a diamond."""
        window = min(70, n // 2 * 2)
        start, mid, end = n - window, n - window // 2, n - 1
        ph, tl = self._pivots(highs, lows, start)
        left_h = [i for i in ph if i < mid]
        left_l = [i for i in tl if i < mid]
        right_h = [i for i in ph if i >= mid]
        right_l = [i for i in tl if i >= mid]
        if min(len(left_h), len(left_l), len(right_h), len(right_l)) < 2:
            return

        expanding = (highs[left_h[-1]] > highs[left_h[0]] and lows[left_l[-1]] < lows[left_l[0]])
        contracting = (highs[right_h[-1]] < highs[right_h[0]] and lows[right_l[-1]] > lows[right_l[0]])
        if not (expanding and contracting):
            return

        top = float(max(highs[left_h[-1]], highs[right_h[0]]))
        bottom = float(min(lows[left_l[-1]], lows[right_l[0]]))
        widest = top - bottom
        if widest <= 0:
            return
        left_t = float((highs[left_h[0]] + lows[left_l[0]]) / 2)
        right_t = float((highs[right_h[-1]] + lows[right_l[-1]]) / 2)
        widest_i = int((left_h[-1] + left_l[-1]) / 2)

        bullish = right_t > left_t
        patterns.append(Pattern(
            "Diamond Bottom" if bullish else "Diamond Top",
            "reversal", bullish, 0.70, n - 1,
            "Volatility expands then collapses – reversal setup",
            target=(right_t + widest) if bullish else (right_t - widest),
            extra={
                "diamond": [
                    [int(min(left_h[0], left_l[0])), left_t],
                    [widest_i, top],
                    [int(max(right_h[-1], right_l[-1])), right_t],
                    [widest_i, bottom],
                ],
                "start": int(start), "end": int(end),
            },
        ))

    def _detect_three_drives(self, closes, peaks, troughs, patterns):
        """Three successive pushes of roughly equal size into exhaustion."""
        for pivots, up in ((peaks, True), (troughs, False)):
            if len(pivots) < 3:
                continue
            d1, d2, d3 = (int(i) for i in pivots[-3:])
            p1, p2, p3 = float(closes[d1]), float(closes[d2]), float(closes[d3])
            stepping = (p1 < p2 < p3) if up else (p1 > p2 > p3)
            if not stepping or d3 - d1 < 12:
                continue
            leg_a, leg_b = abs(p2 - p1), abs(p3 - p2)
            if leg_a <= 0 or not (0.6 <= leg_b / leg_a <= 1.6):
                continue        # the drives have to be comparable in size
            patterns.append(Pattern(
                "Three Drives (Top)" if up else "Three Drives (Bottom)",
                "reversal", not up, 0.72, d3,
                "Three measured pushes – trend exhaustion",
                target=p1,
                extra={"drives": [[d1, p1], [d2, p2], [d3, p3]], "at": "high" if up else "low"},
            ))

    def _detect_island(self, highs, lows, closes, n, patterns):
        """A cluster of bars stranded by a gap on both sides.

        The exit gap is what completes the pattern, so the island itself always
        sits at least one bar back from the right edge.
        """
        # Only the recent tail is worth scanning; an island from months ago is
        # history, not a signal.
        for end in range(n - 2, max(1, n - 40), -1):
            for size in range(1, 6):
                start = end - size + 1
                if start < 1:
                    break
                isle_h = float(highs[start:end + 1].max())
                isle_l = float(lows[start:end + 1].min())
                before_h, before_l = float(highs[start - 1]), float(lows[start - 1])
                after_h, after_l = float(highs[end + 1]), float(lows[end + 1])

                if isle_l > before_h and isle_l > after_h:
                    patterns.append(Pattern(
                        "Island Reversal Top", "reversal", False, 0.80, end + 1,
                        f"{size}-bar cluster stranded above gaps on both sides",
                        target=before_l,
                        extra={"start": int(start), "end": int(end),
                               "top": isle_h, "bottom": isle_l},
                    ))
                    return
                if isle_h < before_l and isle_h < after_l:
                    patterns.append(Pattern(
                        "Island Reversal Bottom", "reversal", True, 0.80, end + 1,
                        f"{size}-bar cluster stranded below gaps on both sides",
                        target=before_h,
                        extra={"start": int(start), "end": int(end),
                               "top": isle_h, "bottom": isle_l},
                    ))
                    return


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
                        extra={
                            "xabcd": [
                                [int(xi), float(xa_price)],
                                [int(ai), float(aa_price)],
                                [int(bi), float(ab_price)],
                                [int(ci), float(ac_price)],
                                [int(di), float(ad_price)],
                            ],
                            "ratios": [round(xb_ratio, 3), round(ac_ratio, 3), round(bd_ratio, 3)],
                        },
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
                    extra={"div": [int(cp1), int(cp2)], "at": "high"},
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
                    extra={"div": [int(ct1), int(ct2)], "at": "low"},
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
                    extra={"div": [int(cp1), int(cp2)], "at": "high"},
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
                    extra={"div": [int(ct1), int(ct2)], "at": "low"},
                ))

        return patterns


class _FormingDetector:
    """Structures that have not completed yet, with the missing pivots projected.

    Everything this emits is a hypothesis about bars that have not printed. The
    payload keeps ``have`` (pivots that really happened) separate from ``future``
    (where the remaining pivots would land), so the chart can draw the confirmed
    half solid and the projection dashed. A viewer should never have to guess
    which part of a drawing is history and which part is a guess.

    Projected indices deliberately run past the end of the data — the drawing
    layer extrapolates the time axis for them.
    """

    MIN_BARS = 30

    def detect(self, opens, highs, lows, closes, atr) -> List[Pattern]:
        out: List[Pattern] = []
        n = len(closes)
        if n < self.MIN_BARS:
            return out

        peaks, troughs = _local_extrema(closes, order=5)
        self._head_shoulders(closes, peaks, troughs, n, out)
        self._doubles(closes, peaks, troughs, n, out)
        self._triples(closes, peaks, troughs, n, out)
        self._apex(highs, lows, closes, atr, n, out)
        return out

    @staticmethod
    def _emit(out, name, bullish, strength, index, desc, kind,
              have, future, level, level_from, target):
        out.append(Pattern(
            name, "forming", bullish, strength, int(index), desc,
            target=None if target is None else float(target),
            extra={
                "projected": True,
                "kind": kind,
                "have": [[int(i), float(p)] for i, p in have],
                "future": [[int(i), float(p)] for i, p in future],
                "level": float(level),
                "level_from": int(level_from),
                "target": None if target is None else float(target),
            },
        ))

    def _head_shoulders(self, closes, peaks, troughs, n, out):
        """Left shoulder and head are in; the right shoulder is not."""
        last = n - 1
        for pivots, up in ((peaks, True), (troughs, False)):
            if len(pivots) < 2:
                continue
            ls, head = int(pivots[-2]), int(pivots[-1])
            if head - ls < 4 or last - head < 3:
                continue
            p_ls, p_head = float(closes[ls]), float(closes[head])
            if up and not p_head > p_ls * 1.02:
                continue
            if not up and not p_head < p_ls * 0.98:
                continue

            rs = head + (head - ls)
            if rs <= last:
                continue        # a symmetric right shoulder was due and never came

            # Route through the armpit, not straight from shoulder to head — a
            # chord across the price action is not the shape of the pattern.
            between = closes[ls:head + 1]
            armpit = ls + int(np.argmin(between) if up else np.argmax(between))
            neck = float(closes[armpit])
            since = closes[head:]
            # Price must have actually left the head without exceeding it.
            if up and (since.max() > p_head or since[-1] > p_head * 0.99):
                continue
            if not up and (since.min() < p_head or since[-1] < p_head * 1.01):
                continue

            height = abs(p_head - neck)
            target = neck - height if up else neck + height
            self._emit(
                out,
                "Head & Shoulders (forming)" if up else "Inverse H&S (forming)",
                not up, 0.58, last,
                f"Left shoulder and head are set; a right shoulder near "
                f"{p_ls:,.2f} in ~{rs - last} bars would complete it",
                "hs",
                have=[(ls, p_ls), (armpit, neck), (head, p_head)],
                future=[(rs, p_ls)],
                level=neck, level_from=ls, target=target,
            )

    def _doubles(self, closes, peaks, troughs, n, out):
        """One peak and its valley are in; the matching peak is not.

        A double top is roughly symmetric about the valley, so the second peak is
        due about as many bars after the valley as the first was before it.
        """
        last = n - 1
        for pivots, up in ((peaks, True), (troughs, False)):
            if len(pivots) < 1:
                continue
            a = int(pivots[-1])
            if last - a < 5:
                continue
            tail = closes[a:]
            v = a + int(np.argmin(tail) if up else np.argmax(tail))
            if v <= a or last - v < 2:
                continue

            p_a, p_v = float(closes[a]), float(closes[v])
            depth = abs(p_a - p_v) / p_a
            if depth < 0.02:
                continue

            proj = v + (v - a)
            if proj <= last:
                continue        # the symmetric second peak is already overdue

            now = float(closes[last])
            # Must be travelling back toward the first peak, not past it.
            if up and not (now > p_v * 1.01 and now < p_a):
                continue
            if not up and not (now < p_v * 0.99 and now > p_a):
                continue

            height = abs(p_a - p_v)
            target = p_v - height if up else p_v + height
            self._emit(
                out,
                "Double Top (forming)" if up else "Double Bottom (forming)",
                not up, 0.55, last,
                f"Retesting the {p_a:,.2f} pivot; a rejection there in "
                f"~{proj - last} bars completes the pattern",
                "double",
                have=[(a, p_a), (v, p_v)],
                future=[(proj, p_a)],
                level=p_v, level_from=a, target=target,
            )

    def _triples(self, closes, peaks, troughs, n, out):
        """Two matching pivots are in; the third is projected."""
        last = n - 1
        for pivots, up in ((peaks, True), (troughs, False)):
            if len(pivots) < 2:
                continue
            a, b = int(pivots[-2]), int(pivots[-1])
            if b - a < 5 or last - b < 3:
                continue
            p_a, p_b = float(closes[a]), float(closes[b])
            if abs(p_a - p_b) / p_a > 0.03:
                continue        # the two pivots are not the same level

            proj = b + (b - a)
            if proj <= last:
                continue
            mid = closes[a:b + 1]
            trough = a + int(np.argmin(mid) if up else np.argmax(mid))
            neck = float(closes[trough])
            level = (p_a + p_b) / 2
            height = abs(level - neck)
            target = neck - height if up else neck + height
            self._emit(
                out,
                "Triple Top (forming)" if up else "Triple Bottom (forming)",
                not up, 0.52, last,
                f"Two rejections at {level:,.2f}; a third in ~{proj - last} bars "
                f"makes it a triple",
                "triple",
                have=[(a, p_a), (trough, neck), (b, p_b)],
                future=[(proj, level)],
                level=neck, level_from=a, target=target,
            )

    def _apex(self, highs, lows, closes, atr, n, out):
        """Converging trendlines that have not broken — where and when they must."""
        window = min(40, n // 2)
        if window < 12:
            return
        start = n - window
        x = np.arange(window, dtype=float)
        c_hi = np.polyfit(x, highs[start:], 1)
        c_lo = np.polyfit(x, lows[start:], 1)

        conv = c_lo[0] - c_hi[0]                 # lines close at this rate per bar
        if conv <= atr[-1] * 0.01:
            return                               # parallel or diverging

        gap_now = float(np.polyval(c_hi, window - 1) - np.polyval(c_lo, window - 1))
        if gap_now <= 0:
            return                               # already crossed — no apex ahead
        bars_to_apex = gap_now / conv
        if not (1 <= bars_to_apex <= window * 1.5):
            return                               # too far out to mean anything

        apex_x = window - 1 + bars_to_apex
        apex_price = float(np.polyval(c_hi, apex_x))
        height = float(np.polyval(c_hi, 0) - np.polyval(c_lo, 0))
        apex_i = start + apex_x

        out.append(Pattern(
            "Apex Breakout (pending)", "forming",
            closes[-1] > (np.polyval(c_hi, window - 1) + np.polyval(c_lo, window - 1)) / 2,
            0.60, n - 1,
            f"Trendlines converge in ~{bars_to_apex:.0f} bars near {apex_price:,.2f}; "
            f"a measured break runs about {height:,.2f}",
            extra={
                "projected": True,
                "kind": "apex",
                "start": int(start), "end": int(n - 1),
                "high_start": float(np.polyval(c_hi, 0)),
                "high_end": float(np.polyval(c_hi, window - 1)),
                "low_start": float(np.polyval(c_lo, 0)),
                "low_end": float(np.polyval(c_lo, window - 1)),
                "apex": [float(apex_i), apex_price],
                "height": height,
            },
        ))


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
        self._form  = _FormingDetector()

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
            ("forming",     lambda: self._form.detect(opens, highs, lows, closes, atr)),
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

        # The pivot loops fire on every consecutive pair, so a long series yields
        # dozens of near-identical Double Tops stretching back months. Keep only
        # the most recent few of each name — the rest are history, and they used
        # to flood the list so badly that the patterns worth seeing got buried.
        seen = set()
        per_name: Dict[str, int] = {}
        unique: List[Pattern] = []
        for p in sorted(all_patterns, key=lambda x: (-x.index, -x.strength)):
            key = (p.name, p.index)
            if key in seen:
                continue
            if per_name.get(p.name, 0) >= MAX_PER_NAME:
                continue
            seen.add(key)
            per_name[p.name] = per_name.get(p.name, 0) + 1
            unique.append(p)

        # Candlestick signals outnumber chart patterns roughly ten to one, so a
        # flat cap would silently drop every triangle and head-and-shoulders on
        # the chart. Rank by category first: what's forming at the right edge,
        # then multi-bar structure, then single-bar signals.
        rank = {"forming": 0, "reversal": 1, "continuation": 1,
                "harmonic": 2, "divergence": 2, "candlestick": 3}
        unique.sort(key=lambda p: (rank.get(p.category, 3), -p.strength, -p.index))
        return [p.to_dict() for p in unique[:MAX_RESULTS]]

    def detect_realtime(self, df: pd.DataFrame, last_n: int = 10) -> List[Dict[str, Any]]:
        """Fast detection on last N bars only (for real-time use)."""
        if df is None or len(df) < 5:
            return []
        # Run on full df but only return patterns in last N bars
        all_pats = self.detect_all(df)
        n = len(df)
        return [p for p in all_pats if p.get("index", 0) >= n - last_n]
