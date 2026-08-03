"""
Desktop chart tests — pattern geometry and the trading-vue payload shape.

No network: the payload is built from a synthetic frame so CI stays offline.
"""

import json

import numpy as np
import pandas as pd
import pytest

from cryptvault.desktop import shapes


@pytest.fixture
def frame():
    n = 140
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series(100 + np.sin(np.linspace(0, 8, n)) * 12 + np.linspace(0, 5, n))
    return pd.DataFrame(
        {
            "open": close.shift(1).fillna(100).values,
            "high": (close + 2.5).values,
            "low": (close - 2.5).values,
            "close": close.values,
            "volume": np.full(n, 1500.0),
        },
        index=idx,
    )


def test_shapes_self_check():
    """The module's own assertions: snapping, bounds, primitive coverage."""
    shapes.demo()


def test_shapes_are_json_serializable_and_in_range(frame):
    from cryptvault.patterns.comprehensive import ComprehensivePatternDetector

    patterns = ComprehensivePatternDetector().detect_all(frame)
    out = shapes.build(frame, patterns)
    assert out, "expected at least the swing structure"

    json.dumps(out)  # must survive the wire

    lo = int(frame.index[0].value // 1_000_000)
    hi = int(frame.index[-1].value // 1_000_000)
    for s in out:
        pts = s.get("pts") or [s["pt"]]
        for t, price in pts:
            assert lo <= t <= hi
            assert np.isfinite(price)


def test_pivots_snap_to_wicks(frame):
    """Diagram vertices must sit on real highs/lows, not on closes."""
    f = shapes._Frame(
        [int(t.value // 1_000_000) for t in frame.index],
        frame["open"].values, frame["high"].values,
        frame["low"].values, frame["close"].values,
    )
    peak = f.peak(40)
    trough = f.trough(40)
    assert peak[1] in set(frame["high"].values)
    assert trough[1] in set(frame["low"].values)
    assert peak[1] > f.c[40] > trough[1]


def test_malformed_extra_does_not_break_the_chart(frame):
    """A bad pivot payload is skipped, never raised."""
    bad = [
        {"name": "Double Top", "index": 50, "bullish": False, "strength": 0.9,
         "extra": {"p1": "nonsense"}},
        {"name": "Head & Shoulders", "index": 60, "bullish": False, "strength": 0.9,
         "extra": {}},
    ]
    assert shapes.build(frame, bad)  # swing structure still there


def test_payload_matches_trading_vue_schema(frame, monkeypatch):
    from cryptvault.desktop import api

    monkeypatch.setattr(api, "fetch", lambda symbol, timeframe: frame)
    payload = api.analyze("TEST-USD", "3M")

    assert payload["chart"]["type"] == "Candles"
    assert len(payload["chart"]["data"][0]) == 6           # [t, o, h, l, c, v]

    types = {o["type"] for o in payload["onchart"]}
    assert {"Channel", "CVShapes"} <= types
    assert payload["offchart"][0]["type"] == "Range"

    overlay = next(o for o in payload["onchart"] if o["type"] == "CVShapes")
    assert overlay["settings"]["shapes"]

    json.dumps(payload)  # the server sends this verbatim
