"""
Pattern geometry → drawing primitives.

The detectors in :mod:`cryptvault.patterns.comprehensive` return pivot indices
and levels in their ``extra`` payload.  This module turns those into a flat list
of shapes expressed in *chart coordinates* — ``[timestamp_ms, price]`` — which
the ``CVShapes`` overlay in the trading-vue chart renders verbatim.

Keeping the geometry here (instead of in JavaScript) means the pattern maths
stays next to the pattern detection, and the browser side is a dumb renderer.

Three rules hold this module together:

1. **Every detected pattern draws.** A pattern you can list but cannot see is
   worse than one you never detected — you know it is there and the chart will
   not show it to you. Structures get their real diagram; single-bar candlestick
   signals get a bracket around the exact candles involved.
2. **Every drawing continues.** A pattern with a target also projects: its
   trigger level carried past the last bar, the measured move drawn as a path,
   and the target marked where and roughly when it would be reached.
3. **Projections are visibly projections.** Anything past the last printed bar
   is dashed and tagged, never solid. Confirmed geometry and hypothesis must
   never look alike.

Primitive kinds:
    poly  {"k":"poly", "pts":[[t,p],...], "c":color, "w":width, "d":dash, "f":fill}
    dot   {"k":"dot",  "pt":[t,p], "c":color, "r":radius}
    text  {"k":"text", "pt":[t,p], "s":string, "c":color, "up":bool}
    mark  {"k":"mark", "pt":[t,p], "c":color, "up":bool}

Every primitive carries a group tag ``g`` — the pattern it belongs to, or ``""``
for the always-on swing structure. The chart draws a handful of groups by
default and isolates one when you click it in the sidebar; drawing sixty at once
is unreadable spaghetti.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np

GREEN = "#26a69a"
RED = "#ef5350"
NEUTRAL = "#8b95a7"
AMBER = "#f0a935"

SNAP = 2               # bars either side to snap a pivot onto the real high/low
MAX_DRAWN = 60         # patterns given geometry — the whole list, so all are clickable
SHOWN_BY_DEFAULT = 4   # ... of which this many are drawn before you pick one
DASH = [6, 4]
DOT_DASH = [2, 4]
GHOST = [3, 5]         # reserved for anything past the last printed bar


class _Frame:
    """Index → (timestamp, price) lookups with pivot snapping.

    Indices past the end of the data are legal: projected pivots live there, and
    :meth:`at` extrapolates the time axis for them at the median bar spacing.
    """

    def __init__(self, times: Sequence[int], opens, highs, lows, closes):
        self.t = list(times)
        self.o, self.h, self.l, self.c = opens, highs, lows, closes
        self.n = len(times)
        diffs = np.diff(self.t) if self.n > 2 else np.array([86_400_000])
        step = float(np.median(diffs)) if len(diffs) else 86_400_000.0
        self.step = step if step > 0 else 86_400_000.0

    def clamp(self, i: int) -> int:
        return max(0, min(self.n - 1, int(i)))

    def time(self, i: int) -> int:
        return self.t[self.clamp(i)]

    def at(self, i: float) -> int:
        """Timestamp for any index, including fractional and future ones."""
        i = float(i)
        if i <= 0:
            return self.t[0]
        if i >= self.n - 1:
            return int(self.t[-1] + self.step * (i - (self.n - 1)))
        lo = int(math.floor(i))
        return int(self.t[lo] + (self.t[lo + 1] - self.t[lo]) * (i - lo))

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

    @property
    def last_close(self) -> float:
        return float(self.c[-1])


# ─────────────────────────────────────────────────────────────────────────────
# Primitive builders
# ─────────────────────────────────────────────────────────────────────────────

def _poly(pts, color, width=2.0, dash=None, fill=None, alpha=None) -> Dict[str, Any]:
    s: Dict[str, Any] = {"k": "poly", "pts": pts, "c": color, "w": width}
    if dash:
        s["d"] = dash
    if fill:
        s["f"] = fill
    if alpha is not None:
        s["a"] = alpha
    return s


def _dot(pt, color, r=4.0) -> Dict[str, Any]:
    return {"k": "dot", "pt": pt, "c": color, "r": r}


def _text(pt, s, color, up=True) -> Dict[str, Any]:
    return {"k": "text", "pt": pt, "s": s, "c": color, "up": up}


def _mark(pt, color, up=True) -> Dict[str, Any]:
    return {"k": "mark", "pt": pt, "c": color, "up": up}


def _line_at(f: _Frame, price: float, i_from: float, i_to: float, color: str, dash=DASH):
    return _poly([[f.at(i_from), price], [f.at(i_to), price]], color, 1.4, dash)


def group_key(pattern: Dict[str, Any]) -> str:
    """Unique id for one detected instance — the name alone collides when the
    same pattern is found twice at different pivots."""
    return f"{pattern.get('name', '?')}@{int(pattern.get('index', -1))}"


def _money(v: float) -> str:
    step = 2 if abs(v) >= 100 else (3 if abs(v) >= 1 else 6)
    return f"{v:,.{step}f}"


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

    return [
        _poly([pa, mid, pb], color, 2.2),                       # the M / W
        _line_at(f, mid[1], a, min(idx + 6, f.n - 1), color),   # neckline
        _dot(pa, color), _dot(pb, color), _dot(mid, color, 3.0),
        _text(pb, name, color, up=top),
    ]


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
    """Two converging, diverging, or parallel trendlines.

    Triangles, wedges, flags, pennants and broadening formations all reduce to
    this: a pair of fitted lines with the price action between them.
    """
    if "start" not in extra or "high_start" not in extra:
        return []
    s = f.clamp(int(extra["start"]))
    e = f.clamp(int(extra.get("end", idx)))
    t0, t1 = f.time(s), f.time(e)
    hi = [[t0, float(extra["high_start"])], [t1, float(extra["high_end"])]]
    lo = [[t0, float(extra["low_start"])], [t1, float(extra["low_end"])]]

    out = [_poly(hi, color, 2.0), _poly(lo, color, 2.0)]
    if fill and not extra.get("diverging"):
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
    handle = [[f.time(e), right], f.trough(hs), [f.time(f.n - 1), f.last_close]]
    rim = (left + right) / 2
    return [
        _poly(arc, color, 2.2),
        _poly(handle, color, 1.8, DOT_DASH),
        _poly([[f.time(s), rim], [f.time(f.n - 1), rim]], color, 1.4, DASH),
        _dot([f.time(bi), bottom], color),
        _text([f.time(e), right], name, color, up=True),
    ]


def _rounding(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    """Saucer or dome — the fitted quadratic, sampled."""
    coef = extra.get("coef")
    if not coef or len(coef) != 3:
        return []
    s, e = f.clamp(extra["arc_start"]), f.clamp(extra["arc_end"])
    if e <= s:
        return []
    # `coef` is fitted in window space; index 0 of the fit is bar `s`.
    step = max(1, (e - s) // 30)
    arc = [[f.time(i), float(np.polyval(coef, i - s))] for i in range(s, e + 1, step)]
    arc.append([f.time(e), float(np.polyval(coef, e - s))])
    vertex = f.clamp(int(extra.get("vertex", (s + e) // 2)))
    rim = float(extra.get("rim", arc[0][1]))

    return [
        _poly(arc, color, 2.2),
        _poly([[f.time(s), rim], [f.time(f.n - 1), rim]], color, 1.4, DASH),
        _dot([f.time(vertex), float(np.polyval(coef, vertex - s))], color, 4.5),
        _text(arc[-1], name, color, up=arc[-1][1] >= rim),
    ]


def _box(f: _Frame, extra: Dict, color: str, name: str, island: bool) -> List[Dict]:
    """Rectangle range, or the stranded cluster of an island reversal."""
    if "top" not in extra or "bottom" not in extra:
        return []
    s, e = f.clamp(extra["start"]), f.clamp(extra["end"])
    top, bottom = float(extra["top"]), float(extra["bottom"])
    half = f.step / 2
    t0, t1 = f.t[s] - half, f.t[e] + half
    corners = [[t0, top], [t1, top], [t1, bottom], [t0, bottom]]

    out: List[Dict] = [_poly(corners, color, 1.6, fill=color)]
    if island:
        # The gaps are the whole pattern — mark the bars either side of them.
        for i, up in ((s - 1, False), (e + 1, True)):
            if 0 <= i < f.n:
                y = float(f.h[i]) if up else float(f.l[i])
                out.append(_mark([f.t[i], y], NEUTRAL, up=up))
    else:
        # A range only matters where it is still in force — extend both edges.
        out.append(_line_at(f, top, e, f.n - 1, color, DOT_DASH))
        out.append(_line_at(f, bottom, e, f.n - 1, color, DOT_DASH))
    out.append(_text([t1, top], name, color, up=True))
    return out


def _diamond(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    pts_raw = extra.get("diamond") or []
    if len(pts_raw) < 4:
        return []
    left, top, right, bottom = [[f.at(i), float(p)] for i, p in pts_raw]
    ring = [left, top, right, bottom, left]
    return [
        _poly(ring, color, 0, fill=color),
        _poly(ring, color, 2.0),
        _dot(top, color, 3.5), _dot(bottom, color, 3.5),
        _text(right, name, color, up=False),
    ]


def _drives(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    """Three measured pushes, with the retracement legs between them."""
    raw = extra.get("drives") or []
    if len(raw) < 3:
        return []
    at_high = extra.get("at") == "high"
    pick = f.peak if at_high else f.trough
    between = f.valley_between if at_high else f.ridge_between

    idxs = [int(i) for i, _ in raw]
    pts, dots = [], []
    for k, i in enumerate(idxs):
        p = pick(i)
        if k:
            pts.append(between(idxs[k - 1], i))
        pts.append(p)
        dots.append(p)

    out: List[Dict] = [_poly(pts, color, 2.2)]
    out += [_dot(d, color) for d in dots]
    for k, d in enumerate(dots):
        out.append(_text(d, str(k + 1), NEUTRAL, up=at_high))
    out.append(_text(dots[-1], name, color, up=at_high))
    return out


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


def _bracket(f: _Frame, idx: int, span: int, color: str, name: str, bull: bool) -> List[Dict]:
    """Box the exact candles a candlestick signal is made of.

    This is the fallback that makes every detection visible. Before it existed a
    Hammer could be listed in the sidebar and simply not appear anywhere on the
    chart, which is the single most confusing thing a pattern tool can do.
    """
    b = f.clamp(idx)
    a = f.clamp(idx - max(1, span) + 1)
    hi = float(np.max(f.h[a:b + 1]))
    lo = float(np.min(f.l[a:b + 1]))
    pad = (hi - lo) * 0.15 or abs(hi) * 0.002
    half = f.step / 2
    t0, t1 = f.t[a] - half, f.t[b] + half

    top, bottom = hi + pad, lo - pad
    anchor = [(t0 + t1) / 2, bottom if bull else top]
    return [
        _poly([[t0, top], [t1, top], [t1, bottom], [t0, bottom]], color, 1.4, fill=color),
        _mark(anchor, color, up=bull),
        _text(anchor, name, color, up=not bull),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Forming patterns — the drawing of a structure that has not happened yet
# ─────────────────────────────────────────────────────────────────────────────

def _forming(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    """Confirmed pivots solid, projected pivots ghosted, trigger level carried."""
    if extra.get("kind") == "apex":
        return _apex(f, extra, color, name)

    have = [[f.at(i), float(p)] for i, p in (extra.get("have") or [])]
    future = [[f.at(i), float(p)] for i, p in (extra.get("future") or [])]
    if not have or not future:
        return []

    now = [f.t[-1], f.last_close]
    level = float(extra.get("level", have[-1][1]))
    level_from = extra.get("level_from", 0)
    up = future[-1][1] >= level

    out: List[Dict] = [
        _poly(have, color, 2.2),                         # what actually printed
        _poly([have[-1], now], NEUTRAL, 1.2, DOT_DASH),  # where price is since
        _poly([now] + future, color, 2.0, GHOST),        # the projected leg
    ]
    out += [_dot(p, color) for p in have]
    out.append(_dot(future[-1], color, 4.5))
    # Trigger level, carried past the projected pivot — this is the line that
    # actually decides whether the pattern resolves.
    out.append(_poly(
        [[f.at(level_from), level], [future[-1][0], level]], color, 1.4, DASH,
    ))
    out.append(_text(future[-1], f"{name} · projected", color, up=up))
    return out


def _apex(f: _Frame, extra: Dict, color: str, name: str) -> List[Dict]:
    """Converging trendlines run forward to their crossing, then both outcomes.

    A pending apex has no direction yet, so drawing one arrow would be a claim
    the data does not support. Both legs are drawn, each in its own colour.
    """
    apex = extra.get("apex")
    if not apex:
        return []
    s, e = f.clamp(extra["start"]), f.clamp(extra["end"])
    ax, ap = float(apex[0]), float(apex[1])
    t_apex = f.at(ax)
    hi_s, hi_e = float(extra["high_start"]), float(extra["high_end"])
    lo_s, lo_e = float(extra["low_start"]), float(extra["low_end"])
    height = abs(float(extra.get("height", hi_e - lo_e)))

    t0, t1 = f.t[s], f.t[e]
    out: List[Dict] = [
        _poly([[t0, hi_s], [t1, hi_e]], NEUTRAL, 2.0),      # printed part
        _poly([[t0, lo_s], [t1, lo_e]], NEUTRAL, 2.0),
        _poly([[t1, hi_e], [t_apex, ap]], NEUTRAL, 1.4, GHOST),   # run to the apex
        _poly([[t1, lo_e], [t_apex, ap]], NEUTRAL, 1.4, GHOST),
        _dot([t_apex, ap], AMBER, 4.5),
    ]

    # Both resolutions, measured from the apex by the pattern's own height.
    run = ax + (ax - (f.n - 1)) or ax + 5
    t_run = f.at(max(run, ax + 3))
    out += [
        _poly([[t_apex, ap], [t_run, ap + height]], GREEN, 1.8, GHOST),
        _poly([[t_apex, ap], [t_run, ap - height]], RED, 1.8, GHOST),
        _text([t_run, ap + height], f"+{_money(height)}", GREEN, up=True),
        _text([t_run, ap - height], f"-{_money(height)}", RED, up=False),
        _text([t_apex, ap], name, AMBER, up=True),
    ]
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Projection — continuing a completed pattern's drawing past the last bar
# ─────────────────────────────────────────────────────────────────────────────

_LEVEL_KEYS = ("neck", "neckline", "level", "rim", "right_rim")


def _level_of(extra: Dict) -> Optional[float]:
    for k in _LEVEL_KEYS:
        v = extra.get(k)
        if v is not None and math.isfinite(float(v)):
            return float(v)
    return None


def _formation_width(extra: Dict, idx: int) -> int:
    """How many bars the pattern took to build.

    Classic measured-move timing: a pattern tends to reach its target in about
    the span it took to form, so the projection borrows its own width rather
    than inventing a horizon.
    """
    starts = [extra.get(k) for k in ("start", "p1", "t1", "ls", "cup_start", "arc_start")]
    starts = [int(s) for s in starts if isinstance(s, (int, float))]
    if extra.get("drives"):
        starts.append(int(extra["drives"][0][0]))
    if extra.get("xabcd"):
        starts.append(int(extra["xabcd"][0][0]))
    if not starts:
        return 10
    return max(4, min(80, idx - min(starts)))


def _projection(f: _Frame, p: Dict[str, Any], color: str) -> List[Dict]:
    """The future half of a completed pattern's drawing."""
    extra = p.get("extra") or {}
    if extra.get("projected"):
        return []                     # forming patterns already draw their own future

    target = p.get("target")
    try:
        target = float(target)
    except (TypeError, ValueError):
        return []
    if not math.isfinite(target) or target <= 0:
        return []

    idx = int(p.get("index", f.n - 1))
    last = f.n - 1
    now = f.last_close
    if abs(target - now) / max(now, 1e-9) < 0.002:
        return []                     # target already met — nothing left to draw

    width = _formation_width(extra, idx)
    t_now, t_end = f.t[last], f.at(last + width)
    up = target >= now

    out: List[Dict] = [
        _poly([[t_now, now], [t_end, target]], color, 1.8, GHOST),
        _dot([t_end, target], color, 4.5),
        _text([t_end, target], f"target {_money(target)}", color, up=up),
    ]

    # The trigger level is what the projection depends on — carry it forward so
    # the two are read together.
    level = _level_of(extra)
    if level is not None and math.isfinite(level):
        out.append(_poly([[f.at(idx), level], [t_end, level]], NEUTRAL, 1.0, DOT_DASH))

    stop = p.get("stop_loss")
    try:
        stop = float(stop)
    except (TypeError, ValueError):
        stop = None
    if stop is not None and math.isfinite(stop) and stop > 0:
        out.append(_poly([[t_now, stop], [t_end, stop]], NEUTRAL, 1.0, GHOST))
        out.append(_text([t_end, stop], f"stop {_money(stop)}", NEUTRAL, up=not up))

    # Trendline patterns keep converging after the last bar; showing where they
    # end up is the most useful thing the projection can add.
    if "high_start" in extra and "start" in extra:
        e = f.clamp(int(extra.get("end", idx)))
        hi_e, lo_e = float(extra["high_end"]), float(extra["low_end"])
        span = max(1, e - f.clamp(int(extra["start"])))
        d_hi = (hi_e - float(extra["high_start"])) / span
        d_lo = (lo_e - float(extra["low_start"])) / span
        ahead = last + width - e
        if ahead > 0:
            out.append(_poly([[f.t[e], hi_e], [t_end, hi_e + d_hi * ahead]], color, 1.2, GHOST))
            out.append(_poly([[f.t[e], lo_e], [t_end, lo_e + d_lo * ahead]], color, 1.2, GHOST))

    return out


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

_DIAGRAMS: Dict[str, Callable[..., List[Dict]]] = {
    "Double Top": lambda f, x, i, c, n: _double(f, x, i, c, True, n),
    "Double Bottom": lambda f, x, i, c, n: _double(f, x, i, c, False, n),
    "Triple Top": lambda f, x, i, c, n: _triple(f, x, c, True, n),
    "Triple Bottom": lambda f, x, i, c, n: _triple(f, x, c, False, n),
    "Head & Shoulders": lambda f, x, i, c, n: _head_shoulders(f, x, i, c, False, n),
    "Inverse Head & Shoulders": lambda f, x, i, c, n: _head_shoulders(f, x, i, c, True, n),
    "Cup & Handle": lambda f, x, i, c, n: _cup_handle(f, x, c, n),
}


def _diagram(f: _Frame, p: Dict[str, Any], color: str) -> List[Dict]:
    """Geometry for one pattern. Never returns empty for a well-formed input —
    anything without a specific diagram falls back to bracketing its candles."""
    name = p.get("name", "?")
    idx = int(p.get("index", f.n - 1))
    extra = p.get("extra") or {}
    bull = bool(p.get("bullish", True))

    if extra.get("projected"):
        return _forming(f, extra, color, name)
    if name in _DIAGRAMS:
        drawn = _DIAGRAMS[name](f, extra, idx, color, name)
        if drawn:
            return drawn
    if "xabcd" in extra:
        return _harmonic(f, extra, color, name)
    if "div" in extra:
        return _divergence(f, extra, color, name)
    if "diamond" in extra:
        return _diamond(f, extra, color, name)
    if "drives" in extra:
        return _drives(f, extra, color, name)
    if "coef" in extra:
        return _rounding(f, extra, color, name)
    if "top" in extra and "bottom" in extra:
        return _box(f, extra, color, name, island="touches_top" not in extra)
    if "high_start" in extra:
        return _channel(f, extra, idx, color, name)
    return _bracket(f, idx, int(extra.get("span", 1) or 1), color, name, bull)


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


def forecast(df, prediction: Optional[Dict[str, Any]], steps: Optional[int] = None) -> Dict[str, Any]:
    """Project the prediction forward from the last bar.

    Returns ``{"shapes": [...], "end": <last timestamp drawn>}``. The cone is a
    volatility envelope, not a calibrated prediction interval — it widens with
    the square root of the horizon and with the model's own lack of confidence.
    This is why the chart labels the overlay beta.
    """
    empty: Dict[str, Any] = {"shapes": [], "end": None}
    if df is None or df.empty or not prediction:
        return empty

    closes = df["close"].values
    n = len(closes)
    if n < 10:
        return empty

    times = [int(ts.value // 1_000_000) for ts in df.index]
    step = int(np.median(np.diff(times))) if n > 2 else 86_400_000
    if step <= 0:
        return empty
    steps = steps or max(6, min(30, n // 10))

    last_t, last_c = times[-1], float(closes[-1])
    target = float(prediction.get("predicted_price", last_c))
    conf = float(prediction.get("confidence", 0.5))
    direction = prediction.get("direction", "NEUTRAL")
    color = {"UP": GREEN, "DOWN": RED}.get(direction, NEUTRAL)

    window = closes[-31:]
    rets = np.diff(window) / window[:-1] if len(window) > 1 else np.array([0.0])
    sigma = float(np.std(rets)) or 0.005
    spread = 1.0 + (1.0 - conf) * 0.8      # less confident, wider cone

    path, upper, lower = [], [], []
    for k in range(steps + 1):
        t = last_t + step * k
        p = last_c + (target - last_c) * (k / steps)
        band = last_c * sigma * math.sqrt(k) * spread
        path.append([t, p])
        upper.append([t, p + band])
        lower.append([t, p - band])

    lo = float(np.min(df["low"].values if "low" in df.columns else closes))
    hi = float(np.max(df["high"].values if "high" in df.columns else closes))

    out = [
        # An outlined envelope reads as a range; a solid wedge just reads as a
        # blob. The cone covers a lot of canvas, so its fill is fainter than a
        # pattern's — it is context for the projection, not the projection.
        _poly(upper + lower[::-1], color, 0, fill=color, alpha=0.045),
        _poly(upper, color, 1.0, DOT_DASH),
        _poly(lower, color, 1.0, DOT_DASH),
        _poly([[last_t, lo], [last_t, hi]], NEUTRAL, 1.0, DOT_DASH),  # now divider
        _poly(path, color, 1.8, DASH),
        _dot(path[-1], color, 4.0),
        _text(path[-1], f"{direction} {_money(target)}", color, up=target >= last_c),
    ]
    for s in out:
        s["g"] = ""            # the forecast overlay is toggled as a whole
    return {"shapes": out, "end": path[-1][0]}


def build(df, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return ``{"shapes", "groups", "defaults", "end"}``.

    ``groups`` lists every pattern that produced geometry — which, by design, is
    every pattern that was detected. ``defaults`` is the handful drawn before the
    user picks one, and ``end`` is the furthest timestamp any projection reaches,
    so the chart can widen its range to include the future.
    """
    empty = {"shapes": [], "groups": [], "defaults": [], "end": None}
    if df is None or df.empty:
        return empty

    times = [int(ts.value // 1_000_000) for ts in df.index]
    col = lambda name: df[name].values if name in df.columns else df["close"].values  # noqa: E731
    f = _Frame(times, col("open"), col("high"), col("low"), df["close"].values)

    shapes: List[Dict[str, Any]] = swing_structure(f)

    valid = [p for p in patterns if isinstance(p.get("index"), int) and 0 <= p["index"] < f.n]
    groups: List[str] = []
    end = f.t[-1]

    for p in valid[:MAX_DRAWN]:
        color = GREEN if p.get("bullish", True) else RED
        try:
            drawn = _diagram(f, p, color)
            drawn += _projection(f, p, color)
        except (KeyError, ValueError, IndexError, TypeError):
            continue    # a malformed pivot payload must never blank the chart
        if not drawn:
            continue

        key = group_key(p)
        for s in drawn:
            s["g"] = key
            for t, _price in (s.get("pts") or [s.get("pt")] or []):
                if t and t > end:
                    end = t
        shapes += drawn
        if key not in groups:
            groups.append(key)

    for s in shapes:
        s.setdefault("g", "")

    # Forming patterns lead: what is about to happen is the reason to look at the
    # right edge. Completed structures fill the rest of the default view.
    rank = {p_key: i for i, p_key in enumerate(groups)}
    forming = [group_key(p) for p in valid[:MAX_DRAWN]
               if (p.get("extra") or {}).get("projected") and group_key(p) in rank]
    others = [g for g in groups if g not in forming]
    defaults = (forming + others)[:SHOWN_BY_DEFAULT]

    return {"shapes": shapes, "groups": groups, "defaults": defaults, "end": end}


def demo() -> None:
    """Self-check: geometry snaps to wicks, every pattern draws, futures project."""
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
         "target": 88.0, "stop_loss": 112.0,
         "extra": {"p1": 20, "p2": 60, "neck": 95.0}},
        {"name": "Head & Shoulders", "index": 90, "bullish": False, "strength": 0.88,
         "target": 85.0,
         "extra": {"ls": 20, "head": 55, "rs": 90, "neckline": 95.0}},
        {"name": "Ascending Triangle", "index": n - 1, "bullish": True, "strength": 0.7,
         "target": 118.0,
         "extra": {"start": 70, "end": n - 1, "high_start": 108.0, "high_end": 108.0,
                   "low_start": 96.0, "low_end": 104.0}},
        {"name": "Gartley (Bullish)", "index": 110, "bullish": True, "strength": 0.8,
         "extra": {"xabcd": [[10, 100.0], [30, 110.0], [50, 104.0],
                             [80, 108.0], [110, 101.0]], "ratios": [0.6, 0.5, 1.3]}},
        {"name": "Rectangle", "index": n - 1, "bullish": True, "strength": 0.68,
         "target": 115.0,
         "extra": {"start": 80, "end": n - 1, "top": 109.0, "bottom": 97.0,
                   "touches_top": 3, "touches_bottom": 2}},
        {"name": "Rounding Bottom", "index": n - 1, "bullish": True, "strength": 0.7,
         "extra": {"arc_start": 40, "arc_end": n - 1, "vertex": 80,
                   "coef": [0.004, -0.5, 105.0], "rim": 106.0}},
        {"name": "Three Drives (Top)", "index": 100, "bullish": False, "strength": 0.72,
         "extra": {"drives": [[40, 105.0], [70, 108.0], [100, 111.0]], "at": "high"}},
        {"name": "Diamond Top", "index": n - 1, "bullish": False, "strength": 0.7,
         "extra": {"diamond": [[60, 103.0], [80, 112.0], [110, 101.0], [80, 94.0]],
                   "start": 60, "end": 110}},
        {"name": "Hammer", "index": 100, "bullish": True, "strength": 0.6,
         "extra": {"span": 1}},
        {"name": "Morning Star", "index": 105, "bullish": True, "strength": 0.88,
         "extra": {"span": 3}},
        {"name": "Double Top (forming)", "index": n - 1, "bullish": False, "strength": 0.55,
         "extra": {"projected": True, "kind": "double",
                   "have": [[70, 110.0], [90, 98.0]], "future": [[130, 110.0]],
                   "level": 98.0, "level_from": 70, "target": 86.0}},
        {"name": "Apex Breakout (pending)", "index": n - 1, "bullish": True, "strength": 0.6,
         "extra": {"projected": True, "kind": "apex", "start": 80, "end": n - 1,
                   "high_start": 112.0, "high_end": 106.0,
                   "low_start": 94.0, "low_end": 102.0,
                   "apex": [128.0, 104.0], "height": 18.0}},
    ]

    out = build(df, pats)
    shapes, groups = out["shapes"], out["groups"]
    assert shapes, "no shapes produced"

    # Rule 1: every pattern draws. This is the whole point of the fallback.
    assert len(groups) == len(pats), (
        f"{len(pats) - len(groups)} pattern(s) produced no geometry: "
        f"{[group_key(p) for p in pats if group_key(p) not in groups]}"
    )
    assert out["defaults"][0].startswith(("Double Top (forming)", "Apex")), \
        f"forming patterns must lead the default view, got {out['defaults']}"
    assert len(out["defaults"]) == SHOWN_BY_DEFAULT

    t_min = min(int(t.value // 1_000_000) for t in idx)
    t_max = max(int(t.value // 1_000_000) for t in idx)

    # Rule 2: patterns with a target project past the last bar.
    assert out["end"] > t_max, "no projection extended beyond the data"
    by_group: Dict[str, List[Dict]] = {}
    for s in shapes:
        by_group.setdefault(s["g"], []).append(s)
    for p in pats:
        if p.get("target") is None:
            continue
        pts = [t for s in by_group[group_key(p)]
               for t, _ in (s.get("pts") or [s.get("pt")])]
        assert max(pts) > t_max, f"{p['name']} has a target but never projects"

    kinds = set()
    for s in shapes:
        kinds.add(s["k"])
        assert s["g"] == "" or s["g"] in groups, f"primitive tagged with unknown group: {s}"
        pts = s.get("pts") or ([s["pt"]] if "pt" in s else [])
        assert pts, f"primitive with no points: {s}"
        for t, price in pts:
            assert t >= t_min, f"timestamp {t} predates the data in {s}"
            assert math.isfinite(price), f"non-finite price in {s}"
    assert {"poly", "dot", "text", "mark"} <= kinds, f"missing primitive kinds: {kinds}"

    # A Double Top must sit on the real highs, not the closes.
    f = _Frame([int(t.value // 1_000_000) for t in idx],
               df["open"].values, df["high"].values, df["low"].values, df["close"].values)
    peak = f.peak(60)
    assert peak[1] == float(df["high"].values[f.snap_high(60)]), "pivot not snapped to swing high"
    # Future indices must extrapolate, not clamp.
    assert f.at(f.n + 9) > f.t[-1], "projected indices must extend the time axis"

    print(f"OK — {len(shapes)} primitives, kinds={sorted(kinds)}, "
          f"{len(groups)}/{len(pats)} patterns drawn, projections reach +"
          f"{(out['end'] - t_max) // 86_400_000}d")


if __name__ == "__main__":
    demo()
