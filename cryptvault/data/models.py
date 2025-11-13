"""
Data Models

Core data structures for price data, ticker information, and market data.
All models use dataclasses for type safety and immutability where appropriate.

Example:
    >>> from cryptvault.data.models import PricePoint, PriceDataFrame
    >>> point = PricePoint(datetime.now(), 50000, 51000, 49000, 50500, 1000000)
    >>> data = PriceDataFrame([point], symbol='BTC', interval='1d')
    >>> closes = data.get_closes()
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import numpy as np


@dataclass(frozen=True)
class PricePoint:
    """
    Single OHLCV price data point.

    Immutable data structure representing a single candlestick or price bar.

    Attributes:
        timestamp: Time of the data point
        open: Opening price
        high: Highest price in period
        low: Lowest price in period
        close: Closing price
        volume: Trading volume

    Example:
        >>> from datetime import datetime
        >>> point = PricePoint(
        ...     timestamp=datetime(2024, 1, 15, 10, 0),
        ...     open=50000.0,
        ...     high=51000.0,
        ...     low=49000.0,
        ...     close=50500.0,
        ...     volume=1000000.0
        ... )
        >>> print(f"Close: ${point.close:,.2f}")
        Close: $50,500.00
    """
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):
        """Validate price point data."""
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) cannot be less than low ({self.low})")
        if self.high < self.open or self.high < self.close:
            raise ValueError(f"High ({self.high}) must be >= open and close")
        if self.low > self.open or self.low > self.close:
            raise ValueError(f"Low ({self.low}) must be <= open and close")
        if self.volume < 0:
            raise ValueError(f"Volume ({self.volume}) cannot be negative")

    @property
    def typical_price(self) -> float:
        """Calculate typical price (HLC/3)."""
        return (self.high + self.low + self.close) / 3

    @property
    def range(self) -> float:
        """Calculate price range (high - low)."""
        return self.high - self.low

    @property
    def body(self) -> float:
        """Calculate candle body size (|close - open|)."""
        return abs(self.close - self.open)

    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish (close > open)."""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Check if candle is bearish (close < open)."""
        return self.close < self.open

    @property
    def is_doji(self) -> bool:
        """Check if candle is doji (close ≈ open)."""
        return abs(self.close - self.open) < (self.range * 0.1)


class PriceDataFrame:
    """
    Container for time series of price data.

    Provides convenient access to price data with various utility methods
    for analysis and manipulation.

    Attributes:
        data: List of PricePoint objects
        symbol: Ticker symbol
        interval: Time interval (e.g., '1d', '1h')

    Example:
        >>> data = PriceDataFrame(price_points, symbol='BTC', interval='1d')
        >>> closes = data.get_closes()
        >>> highs = data.get_highs()
        >>> print(f"Data points: {len(data)}")
    """

    def __init__(
        self,
        data: List[PricePoint],
        symbol: str = "",
        interval: str = "1d"
    ) -> None:
        """
        Initialize price data frame.

        Args:
            data: List of PricePoint objects
            symbol: Ticker symbol
            interval: Time interval

        Raises:
            ValueError: If data is empty or invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")

        self.data = data
        self.symbol = symbol.upper()
        self.interval = interval
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate data integrity."""
        if not all(isinstance(p, PricePoint) for p in self.data):
            raise ValueError("All data points must be PricePoint instances")

        # Check chronological order
        for i in range(1, len(self.data)):
            if self.data[i].timestamp <= self.data[i-1].timestamp:
                raise ValueError("Data points must be in chronological order")

    def __len__(self) -> int:
        """Return number of data points."""
        return len(self.data)

    def __getitem__(self, index: int) -> PricePoint:
        """Get data point by index."""
        return self.data[index]

    def __repr__(self) -> str:
        """Return string representation."""
        return f"PriceDataFrame(symbol='{self.symbol}', interval='{self.interval}', points={len(self)})"

    def get_closes(self) -> List[float]:
        """
        Get closing prices.

        Returns:
            List of closing prices

        Example:
            >>> closes = data.get_closes()
            >>> avg_close = sum(closes) / len(closes)
        """
        return [point.close for point in self.data]

    def get_highs(self) -> List[float]:
        """Get high prices."""
        return [point.high for point in self.data]

    def get_lows(self) -> List[float]:
        """Get low prices."""
        return [point.low for point in self.data]

    def get_opens(self) -> List[float]:
        """Get opening prices."""
        return [point.open for point in self.data]

    def get_volumes(self) -> List[float]:
        """Get volumes."""
        return [point.volume for point in self.data]

    def get_timestamps(self) -> List[datetime]:
        """Get timestamps."""
        return [point.timestamp for point in self.data]

    def get_typical_prices(self) -> List[float]:
        """Get typical prices (HLC/3)."""
        return [point.typical_price for point in self.data]

    def slice(self, start: Optional[int] = None, end: Optional[int] = None) -> 'PriceDataFrame':
        """
        Get slice of data.

        Args:
            start: Start index (inclusive)
            end: End index (exclusive)

        Returns:
            New PriceDataFrame with sliced data
        """
        return PriceDataFrame(
            self.data[start:end],
            symbol=self.symbol,
            interval=self.interval
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'symbol': self.symbol,
            'interval': self.interval,
            'data_points': len(self),
            'start_time': self.data[0].timestamp.isoformat(),
            'end_time': self.data[-1].timestamp.isoformat(),
            'data': [
                {
                    'timestamp': p.timestamp.isoformat(),
                    'open': p.open,
                    'high': p.high,
                    'low': p.low,
                    'close': p.close,
                    'volume': p.volume
                }
                for p in self.data
            ]
        }

    def to_numpy(self) -> Dict[str, np.ndarray]:
        """
        Convert to NumPy arrays.

        Returns:
            Dictionary of NumPy arrays
        """
        return {
            'open': np.array(self.get_opens()),
            'high': np.array(self.get_highs()),
            'low': np.array(self.get_lows()),
            'close': np.array(self.get_closes()),
            'volume': np.array(self.get_volumes())
        }

    @property
    def start_time(self) -> datetime:
        """Get start time of data."""
        return self.data[0].timestamp

    @property
    def end_time(self) -> datetime:
        """Get end time of data."""
        return self.data[-1].timestamp

    @property
    def current_price(self) -> float:
        """Get most recent closing price."""
        return self.data[-1].close

    @property
    def price_change(self) -> float:
        """Get absolute price change from start to end."""
        return self.data[-1].close - self.data[0].close

    @property
    def price_change_percent(self) -> float:
        """Get percentage price change from start to end."""
        return (self.price_change / self.data[0].close) * 100

    @property
    def high_price(self) -> float:
        """Get highest price in dataset."""
        return max(self.get_highs())

    @property
    def low_price(self) -> float:
        """Get lowest price in dataset."""
        return min(self.get_lows())

    @property
    def avg_volume(self) -> float:
        """Get average volume."""
        return sum(self.get_volumes()) / len(self)


@dataclass
class TickerInfo:
    """
    Ticker metadata and information.

    Contains metadata about a ticker symbol including name, type,
    exchange, and other relevant information.

    Attributes:
        symbol: Ticker symbol
        name: Full name
        type: Asset type (crypto, stock, etf)
        exchange: Exchange name
        currency: Trading currency
        market_cap: Market capitalization (optional)
        description: Description (optional)

    Example:
        >>> info = TickerInfo(
        ...     symbol='BTC',
        ...     name='Bitcoin',
        ...     type='crypto',
        ...     exchange='Binance',
        ...     currency='USD'
        ... )
    """
    symbol: str
    name: str
    type: str  # 'crypto', 'stock', 'etf'
    exchange: str
    currency: str = 'USD'
    market_cap: Optional[float] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ticker info."""
        self.symbol = self.symbol.upper()
        valid_types = ['crypto', 'stock', 'etf', 'forex', 'commodity']
        if self.type.lower() not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")


@dataclass
class MarketData:
    """
    Complete market data container.

    Combines price data with ticker information and additional metadata.

    Attributes:
        price_data: Price data frame
        ticker_info: Ticker information
        fetch_time: Time data was fetched
        source: Data source name

    Example:
        >>> market_data = MarketData(
        ...     price_data=price_df,
        ...     ticker_info=ticker_info,
        ...     fetch_time=datetime.now(),
        ...     source='yfinance'
        ... )
    """
    price_data: PriceDataFrame
    ticker_info: TickerInfo
    fetch_time: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def symbol(self) -> str:
        """Get ticker symbol."""
        return self.ticker_info.symbol

    @property
    def current_price(self) -> float:
        """Get current price."""
        return self.price_data.current_price

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'current_price': self.current_price,
            'price_change': self.price_data.price_change,
            'price_change_percent': self.price_data.price_change_percent,
            'ticker_info': {
                'name': self.ticker_info.name,
                'type': self.ticker_info.type,
                'exchange': self.ticker_info.exchange,
                'currency': self.ticker_info.currency
            },
            'price_data': {
                'interval': self.price_data.interval,
                'data_points': len(self.price_data),
                'start_time': self.price_data.start_time.isoformat(),
                'end_time': self.price_data.end_time.isoformat()
            },
            'fetch_time': self.fetch_time.isoformat(),
            'source': self.source,
            'metadata': self.metadata
        }
