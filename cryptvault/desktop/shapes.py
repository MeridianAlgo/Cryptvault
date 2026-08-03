"""
Pattern geometry → drawing primitives.

The detectors in :mod:`cryptvault.patterns.comprehensive` return pivot indices
in their ``extra`` payload.  This module turns those into a flat list of shapes
expressed in *chart coordinates* — ``[timestamp_ms, price]`` — which the
``CVShapes`` overlay in the trading-vue chart renders verbatim.

Keeping the geometry here (instead of in JavaScript) means the pattern maths
stays next to the pattern detection, and the browser side is a dumb renderer.

Primitive kinds:
    poly  {"k":"poly", "pts":[[t,p],...], "c":color, "w":width, "d":dash, "f":fill}
    dot   {"k":"dot",  "pt":[t,p], "c":color, "r":radius}
    text  {"k":"text", "pt":[t,p], "s":string, "c":color, "up":bool}
    mark  {"k":"mark", "pt":[t,p], "c":color, "up":bool}
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

GREEN = "#26a69a"
RED = "#ef5350"
NEUTRAL = "#8b95a7"
SNAP = 2          # bars either side to snap a pivot onto the real high/low
MAX_SHAPED = 6    # geometric patterns drawn as diagrams
MAX_MARKERS = 8   # candlestick patterns drawn as markers
DASH = [6, 4]
DOT_DASH = [2, 4]


class _Frame:
    """Index → (timestamp, price) lookups with pivot snapping."""

    def __init__(self, times: Sequence[int], opens, highs, lows, closes):
        self.t = times
        self.o, self.h, self.l, self.c = opens, highs, lows, closes
        self.n = len(times)

    def clamp(self, i: int) -> int:
        return max(0, min(self.n - 1, int(i)))

    def time(self, i: int) -> int:
        return self.t[self.clamp(i)]

    def snap_high(self, i: int) -> int:
        """Index of the true swing high within ±SNAP bars of ``i``."""
        i = self.clamp(i)
        lo, hi = max(0, i - SNAP), min(self.n, i + SNAP + 1)
        return lo + int(np.argmax(self.h[lo:hi]))

    def snap_low(self, i: int) -> int:
        i = self.clamp(i)
        lo, hi = max(0, i - SNAP), min(self.n, i + SNAP + 1)
        return lo + int(np.argmin(self.l[lo:hi]))

    def peak(self, i: int):
        """(t, price) of the swing high near ``i`` — sits on the wick."""
        j = self.snap_high(i)
        return [self.t[j], float(self.h[j])]

    def trough(self, i: int):
        j = self.snap_low(i)
        return [self.t[j], float(self.l[j])]

    def valley_between(self, a: int, b: int):
        """Lowest low strictly between two peaks."""
        a, b = self.clamp(a), self.clamp(b)
        if b <= a + 1:
            return self.trough(a)
        j = a + 1 + int(np.argmin(self.l[a + 1:b]))
        return [self.t[j], float(self.l[j])]

    def ridge_between(self, a: int, b: int):
        """Highest high strictly between two troughs."""
        a, b = self.clamp(a), self.clamp(b)
        if b <= a + 1:
            return self.peak(a)
        j = a + 1 + int(np.argmax(self.h[a + 1:b]))
        return [self.t[j], float(self.h[j])]


# ─────────────────────────────────────────────────────────────────────────────
# Primitive builders
# ─────────────────────────────────────────────────────────────────────────────

def _poly(pts, color, width=2.0, dash=None, fill=None) -> Dict[str, Any]:
    s: Dict[str, Any] = {"k": "poly", "pts": pts, "c": color, "w": width}
    if dash:
        s["d"] = dash
    if fill:
        s["f"] = fill
    return s


def _dot(pt, color, r=4.0) -> Dict[str, Any]:
    return {"k": "dot", "pt": pt, "c": color, "r": r}


def _text(pt, s, color, up=True) -> Dict[str, Any]:
    return {"k": "text", "pt": pt, "s": s, "c": color, "up": up}


def _mark(pt, color, up=True) -> Dict[str, Any]:
    return {"k": "mark", "pt": pt, "c": color, "up": up}


def _line_at(f: _Frame, price: float, i_from: int, i_to: int, color: str, dash=DASH):
    return _poly([[f.time(i_from), price], [f.time(i_to), price]], color, 1.4, dash)


# ─────────────────────────────────────────────────────────────────────────────
# Per-pattern diagrams
# ─────────────────────────────────────────────────────────────────────────────

def _double(f: _Frame, extra: Dict, idx: int, color: str, top: bool, name: str) -> List[Dict]:
    a_key, b_key = ("p1", "p2") if top else ("t1", "t2")
    if a_key not in extra or b_key not in extra:
        return []
    a, b = int(extra[a_key]), int(extra[b_key])
    pa = f.peak(a) if top else f.trough(a)
    pb = f.peak(b) if top else f.trough(b)
    mid = f.valley_between(a, b) if top else f.ridge_between(a, b)

    out = [
        _poly([pa, mid, pb], color, 2.2),                       # the M / W
        _line_at(f, mid[1], a, min(idx + 6, f.n - 1), color),   # neckline
        _dot(pa, color), _dot(pb, color), _dot(mid, color, 3.0),
        _text(pb, name, color, up=top),
    ]
    return out


def _triple(f: _Frame, extra: Dict, color: str, top: bool, name: str) -> List[Dict]:
    idxs = [extra.get("p1"), extra.get("p2"), extra.get("p3")]
    idxs = [int(i) for i in idxs if i is not None]
    if len(idxs) < 3:
        return []
    pts, dots = [], []
    for k, i in enumerate(idxs):
        p = f.peak(i) if top else f.trough(i)
        if k:
            pts.append(f.valley_between(idxs[k - 1], i) if top else f.ridge_between(idxs[k - 1], i))
        pts.append(p)
        dots.append(p)
    necks = [p[1] for j, p in enumerate(pts) if j % 2]
    neck = (min(necks) if top else max(necks)) if necks else pts[0][1]
    return [
        _poly(pts, color, 2.2),
        _poly([[pts[0][0], neck], [pts[-1][0], neck]], color, 1.4, DASH),
        *[_dot(d, color) for d in dots],
        _text(dots[-1], name, color, up=top),
    ]


def _head_shoulders(f: _Frame, extra: Dict, idx: int, color: str, inverse: bool, name: str) -> List[Dict]:
    if "ls" not in extra:
        return []
    ls, head, rs = int(extra["ls"]), int(extra["head"]), int(extra["rs"])
    pick = f.trough if inverse else f.peak
    between = f.ridge_between if inverse else f.valley_between

    p_ls, p_h, p_rs = pick(ls), pick(head), pick(rs)
    n1 = between(ls, head)
    n2 = between(head, rs)

    # Real necklines slope — draw through both armpits and extend past the pattern.
    span = max(1, n2[0] - n1[0])
    slope = (n2[1] - n1[1]) / span
    t_end = f.time(min(idx + 8, f.n - 1))
    neck_end = n1[1] + slope * (t_end - n1[0])

    return [
        _poly([p_ls, n1, p_h, n2, p_rs], color, 2.2),
        _poly([n1, [t_end, neck_end]], color, 1.6, DASH),
        _dot(p_ls, color), _dot(p_h, color, 5.0), _dot(p_rs, color),
        _text(p_ls, "LS", NEUTRAL, up=not inverse),
        _text(p_h, name, color, up=not inverse),
        _text(p_rs, "RS", NEUTRAL, up=not inverse),
    ]


def _channel(f: _Frame, extra: Dict, idx: int, color: str, name: str, fill: bool = True) -> List[Dict]:
    """Two converging/parallel trendlines — triangles, wedges, flags, pennants."""
    if "start" not in extra:
        return []
    s = f.clamp(int(extra["start"]))
    e = f.clamp(int(extra.get("end", idx)))
    t0, t1 = f.time(s), f.time(e)
    hi = [[t0, float(extra["high_start"])], [t1, float(extra["high_end"])]]
    lo = [[t0, float(extra["low_start"])], [t1, float(extra["low_end"])]]

    out = [_poly(hi, color, 2.0), _poly(lo, color, 2.0)]
    if fill:
        out.insert(0, _poly([hi[0], hi[1], lo[1], lo[0]], color, 0, fill=color))
    if "pole_start" in extra:                       # flag / pennant pole
        ps, pe = int(extra["pole_start"]), int(extra["pole_end"])
        a = f.trough(ps) if extra["low_end"] >= extra["low_start"] else f.peak(ps)
        b = f.peak(pe) if a[1] < float(extra["high_start"]) else f.trough(pe)
        out.append(_poly([a, b], color, 2.4))
    out.append(_text(hi[1], name, color, up=True))
    return out


def _cup_handle(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    """Parabolic cup through rim-bottom-rim, plus the handle pullback."""
    if "cup_start" not in extra:
        return []
    s, bi, e = f.clamp(extra["cup_start"]), f.clamp(extra["cup_bottom"]), f.clamp(extra["cup_end"])
    if not (s < bi < e):
        return []
    left, bottom, right = float(extra["left_rim"]), float(extra["bottom"]), float(extra["right_rim"])

    # Fit a parabola through (s,left) (bi,bottom) (e,right) and sample it.
    coef = np.polyfit([s, bi, e], [left, bottom, right], 2)
    arc = [[f.time(i), float(np.polyval(coef, i))] for i in range(s, e + 1, max(1, (e - s) // 24))]
    arc.append([f.time(e), right])

    hs = f.clamp(extra["handle_start"])
    handle = [[f.time(e), right], f.trough(hs), [f.time(f.n - 1), float(f.c[-1])]]
    rim = (left + right) / 2
    return [
        _poly(arc, color, 2.2),
        _poly(handle, color, 1.8, DOT_DASH),
        _poly([[f.time(s), rim], [f.time(f.n - 1), rim]], color, 1.4, DASH),
        _dot([f.time(bi), bottom], color),
        _text([f.time(e), right], name, color, up=True),
    ]


def _harmonic(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    pts_raw = extra.get("xabcd") or []
    if len(pts_raw) < 5:
        return []
    pts = [[f.time(int(i)), float(p)] for i, p in pts_raw]
    labels = ["X", "A", "B", "C", "D"]
    out = [
        _poly(pts, color, 2.0),
        # XABCD legs shade the two triangles that define the pattern.
        _poly([pts[0], pts[1], pts[2]], color, 0, fill=color),
        _poly([pts[2], pts[3], pts[4]], color, 0, fill=color),
    ]
    for (pt, lab) in zip(pts, labels):
        out.append(_dot(pt, color, 3.5))
        out.append(_text(pt, lab, NEUTRAL, up=pt[1] >= pts[0][1]))
    out.append(_text(pts[4], name, color, up=False))
    return out


def _divergence(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    d = extra.get("div") or []
    if len(d) < 2:
        return []
    at_high = extra.get("at") == "high"
    a = f.peak(d[0]) if at_high else f.trough(d[0])
    b = f.peak(d[1]) if at_high else f.trough(d[1])
    return [
        _poly([a, b], color, 2.0, DOT_DASH),
        _dot(a, color, 3.5), _dot(b, color, 3.5),
        _text(b, name, color, up=at_high),
    ]


_DIAGRAMS = {
    "Double Top": lambda f, x, i, c, n: _double(f, x, i, c, True, n),
    "Double Bottom": lambda f, x, i, c, n: _double(f, x, i, c, False, n),
    "Triple Top": lambda f, x, i, c, n: _triple(f, x, c, True, n),
    "Triple Bottom": lambda f, x, i, c, n: _triple(f, x, c, False, n),
    "Head & Shoulders": lambda f, x, i, c, n: _head_shoulders(f, x, i, c, False, n),
    "Inverse Head & Shoulders": lambda f, x, i, c, n: _head_shoulders(f, x, i, c, True, n),
    "Cup & Handle": lambda f, x, i, c, n: _cup_handle(f, x, c, n),
}

_CHANNELS = {
    "Symmetrical Triangle", "Ascending Triangle", "Descending Triangle",
    "Rising Wedge", "Falling Wedge", "Bull Flag", "Bear Flag",
    "Bull Pennant", "Bear Pennant",
}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def swing_structure(f: _Frame, order: Optional[int] = None) -> List[Dict]:
    """Pivot dots plus fitted support/resistance trendlines."""
    if f.n < 15:
        return []
    order = order or max(3, f.n // 30)
    highs_i, lows_i = [], []
    for i in range(order, f.n - order):
        w = slice(i - order, i + order + 1)
        if f.h[i] == f.h[w].max():
            highs_i.append(i)
        if f.l[i] == f.l[w].min():
            lows_i.append(i)

    out: List[Dict] = []
    out += [_dot([f.t[i], float(f.h[i])], RED, 2.5) for i in highs_i]
    out += [_dot([f.t[i], float(f.l[i])], GREEN, 2.5) for i in lows_i]

    for sel, series, color in ((highs_i, f.h, RED), (lows_i, f.l, GREEN)):
        if len(sel) < 2:
            continue
        use = sel[-3:] if len(sel) >= 3 else sel[-2:]
        coef = np.polyfit(use, [float(series[i]) for i in use], 1)
        a, b = use[0], f.n - 1
        out.append(_poly(
            [[f.t[a], float(np.polyval(coef, a))], [f.t[b], float(np.polyval(coef, b))]],
            color, 1.2, DASH,
        ))
    return out


def build(df, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return the full shape list for a dataframe + detected patterns."""
    if df is None or df.empty:
        return []

    times = [int(ts.value // 1_000_000) for ts in df.index]
    col = lambda name: df[name].values if name in df.columns else df["close"].values  # noqa: E731
    f = _Frame(times, col("open"), col("high"), col("low"), df["close"].values)

    shapes: List[Dict[str, Any]] = swing_structure(f)

    valid = [p for p in patterns if isinstance(p.get("index"), int) and 0 <= p["index"] < f.n]
    strength = lambda p: float(p.get("strength", p.get("confidence", 0)) or 0)  # noqa: E731

    shaped = sorted((p for p in valid if p.get("extra")), key=strength, reverse=True)[:MAX_SHAPED]
    markers = sorted((p for p in valid if not p.get("extra")), key=strength, reverse=True)[:MAX_MARKERS]

    for p in shaped:
        name, idx = p.get("name", "?"), int(p["index"])
        color = GREEN if p.get("bullish", True) else RED
        extra = p["extra"]
        try:
            if name in _DIAGRAMS:
                shapes += _DIAGRAMS[name](f, extra, idx, color, name)
            elif name in _CHANNELS:
                shapes += _channel(f, extra, idx, color, name)
            elif "xabcd" in extra:
                shapes += _harmonic(f, extra, color, name)
            elif "div" in extra:
                shapes += _divergence(f, extra, color, name)
        except (KeyError, ValueError, IndexError, TypeError):
            continue    # a malformed pivot payload must never blank the chart

        target = p.get("target")
        if target and math.isfinite(float(target)):
            shapes.append(_poly(
                [[f.time(idx), float(target)], [f.time(f.n - 1), float(target)]],
                color, 1.0, DOT_DASH,
            ))

    for p in markers:
        idx = int(p["index"])
        bull = p.get("bullish", True)
        color = GREEN if bull else RED
        y = float(f.l[idx]) * 0.995 if bull else float(f.h[idx]) * 1.005
        shapes.append(_mark([f.t[idx], y], color, up=bull))

    return shapes


def demo() -> None:
    """Self-check: geometry snaps to wicks and every primitive is well-formed."""
    import pandas as pd

    n = 120
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series(100 + np.sin(np.linspace(0, 6, n)) * 10)
    df = pd.DataFrame({
        "open": close.shift(1).fillna(100).values,
        "high": (close + 2).values,
        "low": (close - 2).values,
        "close": close.values,
        "volume": np.full(n, 1000.0),
    }, index=idx)

    pats = [
        {"name": "Double Top", "index": 60, "bullish": False, "strength": 0.9,
         "extra": {"p1": 20, "p2": 60, "neck": 95.0}},
        {"name": "Head & Shoulders", "index": 90, "bullish": False, "strength": 0.88,
         "extra": {"ls": 20, "head": 55, "rs": 90, "neckline": 95.0}},
        {"name": "Ascending Triangle", "index": n - 1, "bullish": True, "strength": 0.7,
         "extra": {"start": 70, "high_start": 108.0, "high_end": 108.0,
                   "low_start": 96.0, "low_end": 104.0}},
        {"name": "Gartley (Bullish)", "index": 110, "bullish": True, "strength": 0.8,
         "extra": {"xabcd": [[10, 100.0], [30, 110.0], [50, 104.0],
                             [80, 108.0], [110, 101.0]], "ratios": [0.6, 0.5, 1.3]}},
        {"name": "Hammer", "index": 100, "bullish": True, "strength": 0.6},
    ]

    shapes = build(df, pats)
    assert shapes, "no shapes produced"

    t_min, t_max = min(int(t.value // 1_000_000) for t in idx), max(int(t.value // 1_000_000) for t in idx)
    kinds = set()
    for s in shapes:
        kinds.add(s["k"])
        pts = s.get("pts") or ([s["pt"]] if "pt" in s else [])
        assert pts, f"primitive with no points: {s}"
        for t, price in pts:
            assert t_min <= t <= t_max, f"timestamp {t} outside data range in {s}"
            assert math.isfinite(price), f"non-finite price in {s}"
    assert {"poly", "dot", "text", "mark"} <= kinds, f"missing primitive kinds: {kinds}"

    # A Double Top must sit on the real highs, not the closes.
    f = _Frame([int(t.value // 1_000_000) for t in idx],
               df["open"].values, df["high"].values, df["low"].values, df["close"].values)
    peak = f.peak(60)
    assert peak[1] == float(df["high"].values[f.snap_high(60)]), "pivot not snapped to swing high"

    print(f"OK — {len(shapes)} primitives, kinds={sorted(kinds)}")


if __name__ == "__main__":
    demo()
