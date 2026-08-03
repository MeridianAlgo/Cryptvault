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
    assert out["shapes"], "expected at least the swing structure"
    assert out["defaults"] == out["groups"][: shapes.SHOWN_BY_DEFAULT]

    json.dumps(out)  # must survive the wire

    lo = int(frame.index[0].value // 1_000_000)
    hi = int(frame.index[-1].value // 1_000_000)
    for s in out["shapes"]:
        assert s["g"] == "" or s["g"] in out["groups"]
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
    out = shapes.build(frame, bad)
    assert out["shapes"]      # swing structure still there
    assert out["groups"] == []   # neither bad pattern produced a diagram


def test_forecast_projects_past_the_last_bar(frame):
    from cryptvault.desktop import api

    prediction = api._predict(frame["close"].values, "3M")
    out = shapes.forecast(frame, prediction, steps=10)

    assert out["shapes"]
    last_bar = int(frame.index[-1].value // 1_000_000)
    assert out["end"] > last_bar, "the projection must extend beyond the data"

    # every primitive belongs to the overlay as a whole, never a pattern group
    assert all(s["g"] == "" for s in out["shapes"])

    # the cone widens with the horizon
    cone = out["shapes"][0]
    n = len(cone["pts"]) // 2
    upper, lower = cone["pts"][:n], cone["pts"][n:][::-1]
    assert upper[0][1] - lower[0][1] < upper[-1][1] - lower[-1][1]

    json.dumps(out)


def test_forecast_is_empty_without_a_prediction(frame):
    assert shapes.forecast(frame, None)["shapes"] == []
    assert shapes.forecast(frame.iloc[:5], {"predicted_price": 1.0})["shapes"] == []


def test_every_timeframe_has_a_valid_yahoo_window():
    from cryptvault.desktop import api

    # Yahoo caps intraday history; a window past the cap returns nothing at all.
    caps = {"1m": 7, "5m": 60, "15m": 60, "1h": 730}
    for label, (period, interval) in api.TIMEFRAMES.items():
        assert period.endswith(("d", "wk", "mo", "y")), label
        if interval in caps:
            days = int(period.rstrip("d"))
            assert days <= caps[interval], f"{label}: {days}d exceeds the {interval} cap"
    assert api.DEFAULT_TF in api.TIMEFRAMES


def test_payload_matches_trading_vue_schema(frame, monkeypatch):
    from cryptvault.desktop import api

    monkeypatch.setattr(api, "fetch", lambda symbol, timeframe: frame)
    payload = api.analyze("TEST-USD", "3M")

    assert payload["chart"]["type"] == "Candles"
    assert len(payload["chart"]["data"][0]) == 6           # [t, o, h, l, c, v]

    types = {o["type"] for o in payload["onchart"]}
    assert {"Channel", "CVShapes"} <= types
    assert payload["offchart"][0]["type"] == "Range"

    forecast = next(o for o in payload["onchart"] if o["name"] == "Forecast (beta)")
    assert forecast["settings"]["display"] is True     # the UI toggles this
    assert forecast["settings"]["shapes"]
    assert payload["forecast_end"] > payload["chart"]["data"][-1][0]
    assert "x" in payload["prediction"]["horizon"]     # e.g. "9 x 3M"

    overlay = next(o for o in payload["onchart"] if o["name"] == "Patterns")
    assert overlay["settings"]["shapes"]
    assert overlay["settings"]["only"] is None      # the UI mutates this to isolate
    assert len(overlay["settings"]["defaults"]) <= shapes.SHOWN_BY_DEFAULT

    drawable = set(overlay["settings"]["groups"])
    for p in payload["patterns"]:
        assert p["drawn"] is (p["group"] in drawable)

    # Two instances of the same pattern must not share a group, or isolating
    # one would draw both.
    keys = [p["group"] for p in payload["patterns"]]
    assert len(keys) == len(set(keys))

    json.dumps(payload)  # the server sends this verbatim
