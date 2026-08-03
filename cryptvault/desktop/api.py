"""
Analysis payload for the desktop chart.

Fetches OHLCV, runs pattern detection and a short-horizon trend estimate, and
shapes everything into the object the trading-vue chart consumes:

    {
      "chart":    {"type": "Candles", "data": [[t,o,h,l,c,v], ...]},
      "onchart":  [Bollinger channel, CVShapes overlay],
      "offchart": [RSI],
      "patterns": [...], "prediction": {...}, "stats": {...}
    }
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from . import shapes

logger = logging.getLogger(__name__)

# label → (yfinance period, interval)
#
# The label is the bar interval, and each one carries a window that keeps the
# bar count sane. Yahoo caps intraday history: 1m to 7 days, 5m/15m to 60,
# 1h to 730 — the windows below stay inside those limits.
TIMEFRAMES: Dict[str, Tuple[str, str]] = {
    "1m": ("1d", "1m"),
    "5m": ("5d", "5m"),
    "15m": ("10d", "15m"),
    "1H": ("30d", "1h"),
    "1M": ("30d", "1d"),
    "3M": ("90d", "1d"),
    "6M": ("180d", "1d"),
    "1Y": ("365d", "1d"),
    "2Y": ("730d", "1wk"),
}
DEFAULT_TF = "3M"

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


def fetch(symbol: str, timeframe: str = DEFAULT_TF) -> pd.DataFrame:
    """Download OHLCV for ``symbol``. Raises ValueError when there is no data."""
    period, interval = TIMEFRAMES.get(timeframe, TIMEFRAMES[DEFAULT_TF])

    import yfinance as yf

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
            onchart.append({
                "name": "Bollinger 20/2", "type": "Channel", "data": band,
                "settings": {"color": "#6c7ae0", "backColor": "#6c7ae012",
                             "lineWidth": 0.8, "legend": False},
            })

    geometry = shapes.build(df, patterns)
    onchart.append({
        "name": "Patterns", "type": "CVShapes", "data": [],
        # `only` is mutated by the UI to isolate a single pattern; it must exist
        # up front so Vue tracks it.
        "settings": {**geometry, "only": None, "z-index": 1, "legend": False},
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
                     "only": None, "display": True, "z-index": 2, "legend": False},
    })

    offchart: List[Dict[str, Any]] = []
    if len(closes) >= 15:
        rsi = _rsi(closes)
        offchart.append({
            "name": "RSI 14", "type": "Range",
            "data": [[times[i], float(rsi[i])] for i in range(len(closes))],
            "settings": {"color": "#3f8cff", "backColor": "#3f8cff08",
                         "bandColor": "#4a5568", "upper": 70, "lower": 30},
        })

    change = float((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] else 0.0
    bull = sum(1 for p in patterns if p.get("bullish"))
    bear = len(patterns) - bull

    # Only patterns that actually produced geometry are clickable in the sidebar.
    drawable = set(geometry["groups"])
    listed = patterns[:40]
    for p in listed:
        p["group"] = shapes.group_key(p)
        p["drawn"] = p["group"] in drawable

    return {
        "symbol": symbol,
        "timeframe": timeframe,
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
        "patterns": listed,
        "prediction": prediction,
        # so the chart can widen its range to include the projection
        "forecast_end": projection["end"],
        "stats": {
            "price": float(closes[-1]),
            "change": change,
            "bars": len(df),
            "patterns": len(patterns),
            "bullish": bull,
            "bearish": bear,
            "signal": "Bullish" if bull > bear else ("Bearish" if bear > bull else "Neutral"),
            "high": float(np.max(highs)),
            "low": float(np.min(lows)),
        },
    }
