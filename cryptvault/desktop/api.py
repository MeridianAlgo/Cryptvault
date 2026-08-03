"""
Analysis payload for the desktop chart.

Fetches OHLCV, runs pattern detection and a short-horizon trend estimate, and
shapes everything into the object the trading-vue chart consumes:

    {
      "chart":    {"type": "Candles", "data": [[t,o,h,l,c,v], ...]},
      "onchart":  [Bollinger channel, CVShapes overlay, Forecast overlay],
      "offchart": [RSI],
      "patterns": [...], "prediction": {...}, "stats": {...}
    }

Prices come from Hyperliquid — the venue itself, so the newest bar is the one
still forming rather than a delayed vendor copy. Anything Hyperliquid does not
list falls back to Yahoo, and the payload always says which was used.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import numpy as np
import pandas as pd

from . import hyperliquid, shapes

logger = logging.getLogger(__name__)


class TF(NamedTuple):
    """One timeframe: the venue interval, how much history, and a Yahoo fallback."""

    hl: str                       # Hyperliquid interval
    bars: int                     # bars requested
    yf: Tuple[str, str]           # (yfinance period, yfinance interval)


# Every label is a *bar interval*, never a date range. The previous mix of the
# two ("15m" next to "3M") meant two controls that looked identical did
# completely different things.
#
# Yahoo caps intraday history — 1m to 7 days, 5m/15m to 60, 1h to 730 — so each
# fallback window stays inside its own limit.
TIMEFRAMES: Dict[str, TF] = {
    "1m":  TF("1m",  720, ("1d",    "1m")),
    "5m":  TF("5m",  576, ("5d",    "5m")),
    "15m": TF("15m", 672, ("60d",   "15m")),
    "1H":  TF("1h",  720, ("60d",   "1h")),
    "4H":  TF("4h",  540, ("360d",  "1h")),
    "1D":  TF("1d",  365, ("365d",  "1d")),
    "1W":  TF("1w",  208, ("1460d", "1wk")),
}
DEFAULT_TF = "1H"

GREEN, RED = shapes.GREEN, shapes.RED


def _rsi(closes: np.ndarray, period: int = 14) -> np.ndarray:
    deltas = np.diff(closes, prepend=closes[0])
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = pd.Series(gains).ewm(alpha=1 / period, adjust=False).mean().values
    avg_loss = pd.Series(losses).ewm(alpha=1 / period, adjust=False).mean().values
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = np.where(avg_loss > 0, avg_gain / avg_loss, 100.0)
    rsi = 100 - 100 / (1 + rs)
    rsi[:period] = 50.0
    return rsi


def _predict(closes: np.ndarray, horizon: str) -> Optional[Dict[str, Any]]:
    """Short-horizon trend forecast from recent momentum and volatility."""
    if len(closes) < 10:
        return None
    recent = closes[-10:]
    momentum = (recent[-1] - recent[0]) / recent[0]
    window = closes[-21:] if len(closes) >= 21 else recent
    returns = np.diff(window) / window[:-1]
    volatility = float(np.std(returns)) if len(returns) else 0.0

    if momentum > 0.005:
        direction = "UP"
    elif momentum < -0.005:
        direction = "DOWN"
    else:
        direction = "NEUTRAL"

    # Stronger momentum relative to noise → higher confidence.
    signal = abs(momentum) / (volatility + 1e-6)
    return {
        "predicted_price": float(closes[-1] * (1 + momentum * 0.3)),
        "direction": direction,
        "confidence": float(max(0.4, min(0.9, 0.45 + signal * 0.05))),
        "horizon": horizon,
        "model": "Trend",
    }


def _detect(df: pd.DataFrame) -> List[Dict[str, Any]]:
    try:
        from ..patterns.comprehensive import ComprehensivePatternDetector
        return ComprehensivePatternDetector().detect_all(df)
    except Exception as e:                              # pragma: no cover - optional deps
        logger.warning("Pattern detection failed: %s", e)
        return []


def _from_yahoo(symbol: str, tf: TF) -> pd.DataFrame:
    import yfinance as yf

    period, interval = tf.yf
    df = yf.Ticker(symbol).history(period=period, interval=interval)
    if df is None or df.empty:
        raise ValueError(f"No data for {symbol}")

    df.columns = [str(c).lower() for c in df.columns]
    df = df.dropna(subset=["close"])
    if df.empty:
        raise ValueError(f"No usable rows for {symbol}")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df


def fetch(symbol: str, timeframe: str = DEFAULT_TF) -> pd.DataFrame:
    """Download OHLCV for ``symbol``.

    Hyperliquid first, Yahoo second. The frame carries ``attrs['source']`` so the
    UI can say where the numbers came from — the two feeds do not always agree,
    and a chart that hides which one it is showing is not trustworthy.

    Raises ValueError when neither source has anything.
    """
    tf = TIMEFRAMES.get(timeframe, TIMEFRAMES[DEFAULT_TF])

    coin = hyperliquid.coin_for(symbol)
    if coin:
        try:
            df = hyperliquid.candles(coin, tf.hl, tf.bars)
            df.attrs["source"] = "Hyperliquid"
            df.attrs["coin"] = coin
            return df
        except hyperliquid.HyperliquidError as e:
            logger.warning("Hyperliquid failed for %s, falling back to Yahoo: %s", symbol, e)

    try:
        df = _from_yahoo(symbol, tf)
    except ImportError as e:
        raise ValueError(
            f"{symbol} is not listed on Hyperliquid, and the Yahoo fallback needs "
            f"yfinance installed. Run: pip install yfinance"
        ) from e
    except ValueError as e:
        # Name the recovery, not just the failure — "no data" alone leaves the
        # user guessing whether they mistyped or the feed is down.
        if coin is None:
            raise ValueError(
                f"No market called {symbol}. Hyperliquid lists {len(hyperliquid.universe() or [])} "
                f"tickers — try BTC, ETH or SOL, or pick one from the rail."
            ) from e
        raise
    df.attrs["source"] = "Yahoo"
    return df


def tick(symbol: str, timeframe: str = DEFAULT_TF) -> Dict[str, Any]:
    """Live price and the bar currently forming — the cheap poll for live mode.

    Deliberately does no pattern work: this runs every few seconds, and a full
    re-analysis on that cadence would burn CPU to redraw geometry that has not
    meaningfully changed.
    """
    symbol = (symbol or "").strip().upper()
    tf = TIMEFRAMES.get(timeframe, TIMEFRAMES[DEFAULT_TF])
    coin = hyperliquid.coin_for(symbol)
    if not coin:
        raise ValueError(f"{symbol} is not listed on Hyperliquid — live mode is unavailable")

    df = hyperliquid.candles(coin, tf.hl, 3)
    last = df.iloc[-1]
    price = hyperliquid.mid(coin) or float(last["close"])
    bar = [
        int(df.index[-1].value // 1_000_000),
        float(last["open"]),
        max(float(last["high"]), price),
        min(float(last["low"]), price),
        price,                                  # the forming bar closes at the live mid
        float(last["volume"]),
    ]
    prev = float(df.iloc[-2]["close"]) if len(df) > 1 else float(last["open"])
    return {
        "symbol": symbol,
        "price": price,
        "bar": bar,
        "change_bar": (price - prev) / prev * 100 if prev else 0.0,
        "source": "Hyperliquid",
        "asof": int(time.time() * 1000),
    }


def markets(limit: int = 12) -> List[Dict[str, Any]]:
    """Live mids for a short watchlist — what the market rail shows."""
    preferred = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "AVAX", "LINK",
                 "SUI", "APT", "ARB", "OP"]
    try:
        live = hyperliquid.mids()
    except hyperliquid.HyperliquidError:
        return []
    return [{"symbol": c, "price": live[c]} for c in preferred if c in live][:limit]


def analyze(symbol: str, timeframe: str = DEFAULT_TF) -> Dict[str, Any]:
    """Full payload for one symbol/timeframe."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol is required")
    if timeframe not in TIMEFRAMES:
        timeframe = DEFAULT_TF

    df = fetch(symbol, timeframe)
    patterns = _detect(df)

    times = [int(ts.value // 1_000_000) for ts in df.index]
    closes = df["close"].values
    opens = df["open"].values if "open" in df.columns else closes
    highs = df["high"].values if "high" in df.columns else closes
    lows = df["low"].values if "low" in df.columns else closes
    vols = df["volume"].values if "volume" in df.columns else np.zeros(len(df))

    ohlcv = [
        [times[i], float(opens[i]), float(highs[i]), float(lows[i]), float(closes[i]), float(vols[i])]
        for i in range(len(df))
    ]

    onchart: List[Dict[str, Any]] = []
    if len(closes) >= 20:
        roll = pd.Series(closes).rolling(20)
        mid, sd = roll.mean().values, roll.std().values
        band = [
            [times[i], float(mid[i] + 2 * sd[i]), float(mid[i]), float(mid[i] - 2 * sd[i])]
            for i in range(len(closes))
            if np.isfinite(mid[i]) and np.isfinite(sd[i])
        ]
        if band:
            # Context, not content. The bands used to be the loudest thing on
            # the chart and the pattern geometry read as decoration over them.
            onchart.append({
                "name": "Bollinger 20/2", "type": "Channel", "data": band,
                "settings": {"color": "#3d4761", "backColor": "#3d476109",
                             "lineWidth": 0.7, "legend": False},
            })

    geometry = shapes.build(df, patterns)
    onchart.append({
        "name": "Patterns", "type": "CVShapes", "data": [],
        # `only` is the list of groups the UI has selected; it must exist up
        # front so Vue tracks it.
        "settings": {**geometry, "only": [], "all": False, "z-index": 1, "legend": False},
    })

    # Horizon is a bar count, not the bar interval — say so in the panel.
    steps = max(6, min(30, len(closes) // 10))
    prediction = _predict(closes, timeframe)
    if prediction:
        prediction["horizon"] = f"{steps} x {timeframe}"
    projection = shapes.forecast(df, prediction, steps)
    onchart.append({
        "name": "Forecast (beta)", "type": "CVShapes", "data": [],
        "settings": {"shapes": projection["shapes"], "defaults": [], "groups": [],
                     "only": [], "all": True, "display": True,
                     "z-index": 2, "legend": False},
    })

    offchart: List[Dict[str, Any]] = []
    if len(closes) >= 15:
        rsi = _rsi(closes)
        offchart.append({
            "name": "RSI 14", "type": "Range",
            "data": [[times[i], float(rsi[i])] for i in range(len(closes))],
            # A fifth of the window is enough for a bounded oscillator; the
            # candles and their geometry need the rest.
            "grid": {"height": 0.2},
            "settings": {"color": "#7b8db0", "backColor": "#7b8db008",
                         "bandColor": "#2a3444", "upper": 70, "lower": 30},
        })

    change = float((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] else 0.0
    bull = sum(1 for p in patterns if p.get("bullish"))
    bear = len(patterns) - bull

    drawable = set(geometry["groups"])
    for p in patterns:
        p["group"] = shapes.group_key(p)
        p["drawn"] = p["group"] in drawable
        p["projected"] = bool((p.get("extra") or {}).get("projected"))
        p["at"] = times[min(int(p.get("index", 0)), len(times) - 1)]
        p.pop("extra", None)     # geometry is already built; the payload stays lean

    forming = [p for p in patterns if p["projected"]]
    end = max(t for t in (geometry["end"], projection["end"], times[-1]) if t)

    # Hyperliquid names its books by the base asset alone, but "BTC" alone does
    # not say what it is priced in. These are all USD-quoted, so say so.
    coin = df.attrs.get("coin")
    display = f"{coin}-USD" if coin else symbol

    return {
        "symbol": symbol,
        "display": display,
        "coin": coin,
        "timeframe": timeframe,
        "source": df.attrs.get("source", "Yahoo"),
        "live": df.attrs.get("source") == "Hyperliquid",
        "asof": int(time.time() * 1000),
        "chart": {
            "type": "Candles",
            "data": ohlcv,
            "settings": {
                "colorCandleUp": GREEN, "colorCandleDw": RED,
                "colorWickUp": GREEN, "colorWickDw": RED,
                "colorVolUp": GREEN + "2e", "colorVolDw": RED + "2e",
            },
        },
        "onchart": onchart,
        "offchart": offchart,
        "patterns": patterns,
        "prediction": prediction,
        # so the chart can widen its range to include every projection
        "forecast_end": projection["end"],
        "draw_end": end,
        "stats": {
            "price": float(closes[-1]),
            "change": change,
            "bars": len(df),
            "patterns": len(patterns),
            "forming": len(forming),
            "bullish": bull,
            "bearish": bear,
            "signal": "Bullish" if bull > bear else ("Bearish" if bear > bull else "Neutral"),
            "high": float(np.max(highs)),
            "low": float(np.min(lows)),
            "volume": float(np.sum(vols)),
        },
    }
