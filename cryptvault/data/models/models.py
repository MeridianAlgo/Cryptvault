"""Data models for price data."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PricePoint:
    """Single price data point."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class PriceDataFrame:
    """Container for price data series."""

    def __init__(self, data: List[PricePoint], symbol: str = "", timeframe: str = "1d"):
        self.data = data
        self.symbol = symbol
        self.timeframe = timeframe

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def get_closes(self) -> List[float]:
        """Get closing prices."""
        return [point.close for point in self.data]

    def get_highs(self) -> List[float]:
        """Get high prices."""
        return [point.high for point in self.data]

    def get_lows(self) -> List[float]:
        """Get low prices."""
        return [point.low for point in self.data]

    def get_volumes(self) -> List[float]:
        """Get volumes."""
        return [point.volume for point in self.data]

    def get_timestamps(self) -> List[datetime]:
        """Get timestamps."""
        return [point.timestamp for point in self.data]
