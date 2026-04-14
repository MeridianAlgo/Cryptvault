"""
Real-time data streaming for CryptVault.

Polls yfinance/ccxt at configurable intervals to simulate live market data.
Runs in a background daemon thread and fires callbacks with new bars.
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    """A single real-time data event."""

    symbol: str
    timestamp: datetime
    price: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    change_pct: float
    bar_df: Optional[pd.DataFrame] = None   # Full OHLCV history for analysis
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    prediction: Optional[Dict[str, Any]] = None


class RealTimeStream:
    """
    Background polling stream for live market data.

    Usage
    -----
    stream = RealTimeStream("BTC-USD", interval_seconds=15)
    stream.subscribe(my_callback)
    stream.start()
    ...
    stream.stop()
    """

    SYMBOL_MAP = {
        # Crypto shortcuts
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
        "BNB": "BNB-USD",
        "ADA": "ADA-USD",
        "XRP": "XRP-USD",
        "DOT": "DOT-USD",
        "DOGE": "DOGE-USD",
        "AVAX": "AVAX-USD",
        "LINK": "LINK-USD",
        "MATIC": "MATIC-USD",
        "LTC": "LTC-USD",
        "ATOM": "ATOM-USD",
        "UNI": "UNI-USD",
        "SHIB": "SHIB-USD",
    }

    def __init__(
        self,
        symbol: str = "BTC-USD",
        interval_seconds: int = 15,
        history_bars: int = 200,
    ):
        self.symbol = self.SYMBOL_MAP.get(symbol.upper(), symbol)
        self.display_symbol = symbol.upper()
        self.interval_seconds = max(5, interval_seconds)
        self.history_bars = history_bars

        self._callbacks: List[Callable[[StreamEvent], None]] = []
        self._error_callbacks: List[Callable[[Exception], None]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_price: Optional[float] = None
        self._running = False
        self._df_cache: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def subscribe(self, callback: Callable[[StreamEvent], None]) -> None:
        """Register a callback for new data events."""
        self._callbacks.append(callback)

    def on_error(self, callback: Callable[[Exception], None]) -> None:
        """Register an error callback."""
        self._error_callbacks.append(callback)

    def start(self) -> None:
        """Start the background polling thread."""
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"stream-{self.symbol}")
        self._thread.start()
        logger.info("RealTimeStream started for %s (poll every %ds)", self.symbol, self.interval_seconds)

    def stop(self) -> None:
        """Stop the polling thread gracefully."""
        self._stop_event.set()
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("RealTimeStream stopped for %s", self.symbol)

    def change_symbol(self, symbol: str) -> None:
        """Switch to a different symbol (restarts stream)."""
        was_running = self._running
        self.stop()
        self.symbol = self.SYMBOL_MAP.get(symbol.upper(), symbol)
        self.display_symbol = symbol.upper()
        self._last_price = None
        self._df_cache = None
        if was_running:
            self.start()

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Main polling loop."""
        while not self._stop_event.is_set():
            try:
                event = self._fetch_latest()
                if event:
                    for cb in self._callbacks:
                        try:
                            cb(event)
                        except Exception as e:
                            logger.error("Callback error: %s", e)
            except Exception as e:
                logger.warning("Stream fetch error: %s", e)
                for cb in self._error_callbacks:
                    try:
                        cb(e)
                    except Exception:
                        pass

            self._stop_event.wait(timeout=self.interval_seconds)

    def _fetch_latest(self) -> Optional[StreamEvent]:
        """Fetch latest OHLCV data and build a StreamEvent."""
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance not installed")
            return None

        ticker = yf.Ticker(self.symbol)

        # Fetch 2 days of 1-minute data for real-time feel
        try:
            df_1m = ticker.history(period="1d", interval="1m")
        except Exception:
            df_1m = pd.DataFrame()

        # Fetch 60 days of daily data for analysis
        try:
            df_daily = ticker.history(period="60d", interval="1d")
        except Exception:
            df_daily = pd.DataFrame()

        if df_1m.empty and df_daily.empty:
            return None

        # Use 1-min for latest price, daily for history analysis
        if not df_1m.empty:
            latest = df_1m.iloc[-1]
            prev = df_1m.iloc[-2] if len(df_1m) > 1 else latest
        else:
            latest = df_daily.iloc[-1]
            prev = df_daily.iloc[-2] if len(df_daily) > 1 else latest

        price = float(latest["Close"])
        prev_close = float(prev["Close"])
        change_pct = ((price - prev_close) / prev_close * 100) if prev_close != 0 else 0.0

        # Use daily df for analysis (stable for pattern/ml)
        analysis_df = df_daily if not df_daily.empty else df_1m
        analysis_df = analysis_df.tail(self.history_bars).copy()

        # Normalize column names
        analysis_df.columns = [c.lower() for c in analysis_df.columns]
        for col in ["open", "high", "low", "close", "volume"]:
            if col not in analysis_df.columns:
                analysis_df[col] = analysis_df.get("close", price)

        self._df_cache = analysis_df

        return StreamEvent(
            symbol=self.display_symbol,
            timestamp=datetime.now(),
            price=price,
            open=float(latest.get("Open", price)),
            high=float(latest.get("High", price)),
            low=float(latest.get("Low", price)),
            close=price,
            volume=float(latest.get("Volume", 0)),
            change_pct=change_pct,
            bar_df=analysis_df,
        )

    def get_cached_df(self) -> Optional[pd.DataFrame]:
        """Return the last fetched DataFrame (for immediate access after start)."""
        return self._df_cache
