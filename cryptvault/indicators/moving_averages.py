"""Moving average calculations."""

from typing import List, Optional


class MovingAverages:
    """Calculate various types of moving averages."""

    def __init__(self):
        pass

    def sma(self, prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return [None] * len(prices)

        sma_values = [None] * (period - 1)

        for i in range(period - 1, len(prices)):
            sma = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(sma)

        return sma_values

    def ema(self, prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return [None] * len(prices)

        ema_values = [None] * (period - 1)

        # Calculate initial SMA
        sma = sum(prices[:period]) / period
        ema_values.append(sma)

        # Calculate multiplier
        multiplier = 2 / (period + 1)

        # Calculate EMA for remaining periods
        for i in range(period, len(prices)):
            ema = (prices[i] - ema_values[-1]) * multiplier + ema_values[-1]
            ema_values.append(ema)

        return ema_values

    def wma(self, prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate Weighted Moving Average."""
        if len(prices) < period:
            return [None] * len(prices)

        wma_values = [None] * (period - 1)

        # Calculate weights
        weights = list(range(1, period + 1))
        weight_sum = sum(weights)

        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            wma = sum(w * p for w, p in zip(weights, window)) / weight_sum
            wma_values.append(wma)

        return wma_values
