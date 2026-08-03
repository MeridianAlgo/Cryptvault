"""
Hyperliquid market data — candles and live mid prices.

The public ``/info`` endpoint needs no key, and it is the venue the price is
actually formed on, so the newest bar is live rather than a delayed vendor
copy. That is what makes the desktop chart's live mode honest.

Standard library only — one POST, JSON in, JSON out.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

INFO_URL = "https://api.hyperliquid.xyz/info"
TIMEOUT = 15
MAX_BARS = 5000                 # venue cap on one candleSnapshot request

# Bar sizes the venue serves, in milliseconds.
INTERVAL_MS: Dict[str, int] = {
    "1m": 60_000,
    "3m": 180_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "2h": 7_200_000,
    "4h": 14_400_000,
    "8h": 28_800_000,
    "12h": 43_200_000,
    "1d": 86_400_000,
    "3d": 259_200_000,
    "1w": 604_800_000,
}

_universe: List[str] = []
_universe_at = 0.0
_universe_lock = threading.Lock()
UNIVERSE_TTL = 600.0


class HyperliquidError(RuntimeError):
    """The venue was unreachable or answered with something unusable."""


def _post(payload: Dict[str, Any]) -> Any:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        INFO_URL, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 - pinned https
            return json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
        raise HyperliquidError(f"Hyperliquid request failed: {e}") from e


def universe() -> List[str]:
    """Perp tickers the venue lists, cached for ten minutes."""
    global _universe, _universe_at
    with _universe_lock:
        if _universe and time.time() - _universe_at < UNIVERSE_TTL:
            return _universe
        meta = _post({"type": "meta"})
        names = [a["name"] for a in (meta or {}).get("universe", []) if a.get("name")]
        if names:
            _universe, _universe_at = names, time.time()
        return _universe


def coin_for(symbol: str) -> Optional[str]:
    """Map a user-typed symbol onto a Hyperliquid ticker, or ``None``.

    ``BTC``, ``btc-usd``, ``BTCUSDT`` and ``BTC/USD`` all resolve to ``BTC``.
    """
    raw = (symbol or "").strip().upper()
    if not raw:
        return None
    head = raw.replace("/", "-").split("-")[0]
    for quote in ("USDT", "USDC", "USD"):
        if head != quote and head.endswith(quote):
            head = head[: -len(quote)]
            break
    try:
        listed = universe()
    except HyperliquidError:
        return None
    if head in listed:
        return head
    # kPEPE, kBONK … the venue prefixes thousand-denominated books with `k`.
    if f"k{head}" in listed:
        return f"k{head}"
    return None


def mids() -> Dict[str, float]:
    """Live mid price per ticker. Spot index keys (``#123``) are dropped."""
    raw = _post({"type": "allMids"})
    if not isinstance(raw, dict):
        raise HyperliquidError("allMids returned an unexpected shape")
    out: Dict[str, float] = {}
    for k, v in raw.items():
        if k.startswith("#"):
            continue
        try:
            out[k] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def mid(coin: str) -> Optional[float]:
    """Live mid for one ticker."""
    return mids().get(coin)


def candles(coin: str, interval: str, bars: int) -> pd.DataFrame:
    """OHLCV for ``coin``, newest bar last, indexed by bar open time (UTC).

    The final row is the bar in progress — that is the point of live mode.
    """
    step = INTERVAL_MS.get(interval)
    if step is None:
        raise HyperliquidError(f"Unsupported interval: {interval}")
    bars = max(20, min(MAX_BARS, int(bars)))

    now = int(time.time() * 1000)
    rows = _post({
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval,
            # One extra bar of slack: the venue aligns the window to bar opens.
            "startTime": now - step * (bars + 1),
            "endTime": now,
        },
    })
    if not rows:
        raise HyperliquidError(f"No {interval} candles for {coin}")

    frame = pd.DataFrame([
        {
            "time": int(r["t"]),
            "open": float(r["o"]),
            "high": float(r["h"]),
            "low": float(r["l"]),
            "close": float(r["c"]),
            "volume": float(r.get("v") or 0.0),
        }
        for r in rows
    ])
    frame = frame.drop_duplicates(subset="time").sort_values("time")
    frame.index = pd.to_datetime(frame.pop("time"), unit="ms", utc=True)
    frame.index.name = None
    return frame


def demo() -> None:
    """Self-check against the live venue. Skips cleanly when offline."""
    try:
        listed = universe()
    except HyperliquidError as e:
        print(f"SKIP — venue unreachable: {e}")
        return

    assert "BTC" in listed, "BTC should always be listed"
    assert coin_for("btc-usd") == "BTC"
    assert coin_for("BTCUSDT") == "BTC"
    assert coin_for("ZZQQXX") is None

    df = candles("BTC", "1h", 48)
    assert len(df) >= 24, f"expected ~48 hourly bars, got {len(df)}"
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.index.is_monotonic_increasing, "bars must be chronological"
    assert (df["high"] >= df["low"]).all(), "high must never print below low"

    price = mid("BTC")
    assert price and price > 0, "no live mid for BTC"
    # The live mid should sit inside the range of the bar still forming.
    last = df.iloc[-1]
    assert last["low"] * 0.9 <= price <= last["high"] * 1.1, "mid detached from the last bar"

    print(f"OK — {len(listed)} tickers, {len(df)} bars, BTC mid {price:,.2f}")


if __name__ == "__main__":
    demo()
