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


@pytest.fixture
def detected(frame):
    from cryptvault.patterns.comprehensive import ComprehensivePatternDetector

    return ComprehensivePatternDetector().detect_all(frame)


def test_shapes_self_check():
    """The module's own assertions: snapping, bounds, every pattern drawn."""
    shapes.demo()


def test_every_detected_pattern_is_drawable(frame, detected):
    """The headline guarantee: nothing is listed that cannot be shown.

    A pattern in the sidebar that draws nothing when clicked is the worst
    failure this tool has — you are told it exists and then shown nothing.
    """
    assert detected, "the fixture should trigger some patterns"
    out = shapes.build(frame, detected)
    drawn = set(out["groups"])
    missing = [p["name"] for p in detected if shapes.group_key(p) not in drawn]
    assert not missing, f"detected but not drawable: {missing}"


def test_candlestick_patterns_bracket_their_own_candles(frame):
    """A three-bar pattern must not be highlighted as a single candle."""
    f = shapes._Frame(
        [int(t.value // 1_000_000) for t in frame.index],
        frame["open"].values, frame["high"].values,
        frame["low"].values, frame["close"].values,
    )
    one = shapes._bracket(f, 60, 1, shapes.GREEN, "Hammer", True)
    three = shapes._bracket(f, 60, 3, shapes.GREEN, "Morning Star", True)

    def width(prims):
        xs = [t for s in prims if s["k"] == "poly" for t, _ in s["pts"]]
        return max(xs) - min(xs)

    assert width(three) > width(one), "span is ignored — every pattern boxes one bar"


def test_shapes_are_json_serializable_and_in_range(frame, detected):
    out = shapes.build(frame, detected)
    assert out["shapes"], "expected at least the swing structure"
    assert len(out["defaults"]) <= shapes.SHOWN_BY_DEFAULT

    json.dumps(out)  # must survive the wire

    lo = int(frame.index[0].value // 1_000_000)
    for s in out["shapes"]:
        assert s["g"] == "" or s["g"] in out["groups"]
        pts = s.get("pts") or [s["pt"]]
        for t, price in pts:
            assert t >= lo, "no geometry may predate the data"
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


def test_future_indices_extend_the_time_axis(frame):
    """Projected pivots live past the last bar and must not clamp onto it."""
    f = shapes._Frame(
        [int(t.value // 1_000_000) for t in frame.index],
        frame["open"].values, frame["high"].values,
        frame["low"].values, frame["close"].values,
    )
    last = f.t[-1]
    assert f.at(f.n - 1) == last
    assert f.at(f.n + 9) == last + f.step * 10
    assert f.time(f.n + 9) == last, "time() still clamps — that is its job"


def test_a_pattern_with_a_target_projects_past_the_last_bar(frame):
    """Rule 2 of the module: every drawing continues."""
    pat = {
        "name": "Double Top", "index": 100, "bullish": False, "strength": 0.8,
        "target": 90.0, "stop_loss": 120.0,
        "extra": {"p1": 60, "p2": 100, "neck": 98.0},
    }
    out = shapes.build(frame, [pat])
    last = int(frame.index[-1].value // 1_000_000)
    assert out["end"] > last

    mine = [s for s in out["shapes"] if s["g"] == shapes.group_key(pat)]
    reach = max(t for s in mine for t, _ in (s.get("pts") or [s["pt"]]))
    assert reach > last, "the target was never projected forward"

    labels = " ".join(s["s"] for s in mine if s["k"] == "text")
    assert "target" in labels and "stop" in labels


def test_forming_patterns_separate_history_from_projection():
    """Confirmed pivots draw solid; projected ones must be dashed."""
    n = 60
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series(np.linspace(100, 110, n))
    df = pd.DataFrame({
        "open": close.values, "high": (close + 1).values,
        "low": (close - 1).values, "close": close.values,
        "volume": np.full(n, 100.0),
    }, index=idx)

    pat = {
        "name": "Double Top (forming)", "index": n - 1, "bullish": False,
        "strength": 0.55, "target": 95.0,
        "extra": {"projected": True, "kind": "double",
                  "have": [[20, 112.0], [35, 104.0]], "future": [[75, 112.0]],
                  "level": 104.0, "level_from": 20, "target": 95.0},
    }
    out = shapes.build(df, [pat])
    mine = [s for s in out["shapes"] if s["g"] == shapes.group_key(pat)]
    last = int(idx[-1].value // 1_000_000)

    solid = [s for s in mine if s["k"] == "poly" and not s.get("d")]
    assert solid, "the confirmed pivots must be drawn solid"
    for s in solid:
        assert max(t for t, _ in s["pts"]) <= last, \
            "a solid line reached into the future — history and guess must look different"

    ghosted = [s for s in mine if s.get("d") and max(t for t, _ in s["pts"]) > last]
    assert ghosted, "the projected leg must extend past the last bar, dashed"


def test_malformed_extra_does_not_break_the_chart(frame):
    """A bad pivot payload falls back to bracketing, never raises."""
    bad = [
        {"name": "Double Top", "index": 50, "bullish": False, "strength": 0.9,
         "extra": {"p1": "nonsense"}},
        {"name": "Head & Shoulders", "index": 60, "bullish": False, "strength": 0.9,
         "extra": {}},
    ]
    out = shapes.build(frame, bad)
    assert out["shapes"]
    json.dumps(out)


def test_forecast_projects_past_the_last_bar(frame):
    from cryptvault.desktop import api

    prediction = api._predict(frame["close"].values, "1H")
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


def test_every_timeframe_is_valid_at_both_sources():
    from cryptvault.desktop import api, hyperliquid

    # Yahoo caps intraday history; a window past the cap returns nothing at all.
    caps = {"1m": 7, "5m": 60, "15m": 60, "1h": 730}
    for label, tf in api.TIMEFRAMES.items():
        assert tf.hl in hyperliquid.INTERVAL_MS, f"{label}: {tf.hl} is not a venue interval"
        assert 20 <= tf.bars <= hyperliquid.MAX_BARS, f"{label}: {tf.bars} bars"
        period, interval = tf.yf
        assert period.endswith(("d", "wk", "mo", "y")), label
        if interval in caps:
            days = int(period.rstrip("d"))
            assert days <= caps[interval], f"{label}: {days}d exceeds the {interval} cap"
    assert api.DEFAULT_TF in api.TIMEFRAMES


def test_symbol_mapping_is_forgiving():
    """However the user types it, the same book should come back."""
    from cryptvault.desktop import hyperliquid

    hyperliquid._universe = ["BTC", "ETH", "kPEPE"]
    hyperliquid._universe_at = float("inf")
    try:
        for typed in ("BTC", "btc", "BTC-USD", "btc/usd", "BTCUSDT", " btc-usdc "):
            assert hyperliquid.coin_for(typed) == "BTC", typed
        assert hyperliquid.coin_for("PEPE") == "kPEPE"
        assert hyperliquid.coin_for("NOSUCHTHING") is None
        assert hyperliquid.coin_for("") is None
    finally:
        hyperliquid._universe, hyperliquid._universe_at = [], 0.0


def test_payload_matches_trading_vue_schema(frame, monkeypatch):
    from cryptvault.desktop import api

    frame.attrs["source"] = "Hyperliquid"
    monkeypatch.setattr(api, "fetch", lambda symbol, timeframe: frame)
    payload = api.analyze("TEST-USD", "1H")

    assert payload["chart"]["type"] == "Candles"
    assert len(payload["chart"]["data"][0]) == 6           # [t, o, h, l, c, v]
    assert payload["source"] == "Hyperliquid" and payload["live"] is True

    types = {o["type"] for o in payload["onchart"]}
    assert {"Channel", "CVShapes"} <= types
    assert payload["offchart"][0]["type"] == "Range"

    forecast = next(o for o in payload["onchart"] if o["name"] == "Forecast (beta)")
    assert forecast["settings"]["display"] is True     # the UI toggles this
    assert forecast["settings"]["shapes"]
    assert payload["forecast_end"] > payload["chart"]["data"][-1][0]
    assert payload["draw_end"] >= payload["forecast_end"]
    assert "x" in payload["prediction"]["horizon"]     # e.g. "9 x 1H"

    overlay = next(o for o in payload["onchart"] if o["name"] == "Patterns")
    assert overlay["settings"]["shapes"]
    assert overlay["settings"]["only"] is None      # the UI mutates these
    assert overlay["settings"]["all"] is False
    assert len(overlay["settings"]["defaults"]) <= shapes.SHOWN_BY_DEFAULT

    # Every listed pattern is clickable, and the panel has what it renders.
    assert payload["patterns"], "the fixture should produce patterns"
    for p in payload["patterns"]:
        assert p["drawn"] is True, f"{p['name']} is listed but not drawable"
        assert "extra" not in p, "raw pivot payload should not reach the browser"
        assert p["at"] >= payload["chart"]["data"][0][0]
        assert p["category"] and isinstance(p["projected"], bool)

    # Two instances of the same pattern must not share a group, or isolating
    # one would draw both.
    keys = [p["group"] for p in payload["patterns"]]
    assert len(keys) == len(set(keys))

    json.dumps(payload)  # the server sends this verbatim
