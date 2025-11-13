"""Technical indicators calculations."""

from typing import List, Optional
import numpy as np


class TechnicalIndicators:
    """Calculate technical indicators like RSI, MACD, etc."""

    def __init__(self):
        pass

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[Optional[float]]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return [None] * len(prices)

        rsi_values = [None] * period

        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]

        # Separate gains and losses
        gains = [max(0, change) for change in changes]
        losses = [abs(min(0, change)) for change in changes]

        # Calculate initial average gain and loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        # Calculate RSI for each period
        for i in range(period, len(prices)):
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)

            # Update averages
            if i < len(gains):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        return rsi_values

    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(prices) < slow:
            return {
                'macd': [None] * len(prices),
                'signal': [None] * len(prices),
                'histogram': [None] * len(prices)
            }

        # Calculate EMAs
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)

        # Calculate MACD line
        macd_line = []
        for i in range(len(prices)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line.append(ema_fast[i] - ema_slow[i])
            else:
                macd_line.append(None)

        # Calculate signal line
        signal_line = self._calculate_ema([m for m in macd_line if m is not None], signal)

        # Pad signal line to match length
        signal_padded = [None] * (len(macd_line) - len(signal_line)) + signal_line

        # Calculate histogram
        histogram = []
        for i in range(len(macd_line)):
            if macd_line[i] is not None and signal_padded[i] is not None:
                histogram.append(macd_line[i] - signal_padded[i])
            else:
                histogram.append(None)

        return {
            'macd': macd_line,
            'signal': signal_padded,
            'histogram': histogram
        }

    def _calculate_ema(self, prices: List[float], period: int) -> List[Optional[float]]:
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

    def calculate_sma(self, prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return [None] * len(prices)

        sma_values = [None] * (period - 1)

        for i in range(period - 1, len(prices)):
            sma = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(sma)

        return sma_values

    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0):
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return {
                'upper': [None] * len(prices),
                'middle': [None] * len(prices),
                'lower': [None] * len(prices)
            }

        middle_band = self.calculate_sma(prices, period)
        upper_band = []
        lower_band = []

        for i in range(len(prices)):
            if middle_band[i] is not None:
                # Calculate standard deviation
                window = prices[max(0, i - period + 1):i + 1]
                std = np.std(window)

                upper_band.append(middle_band[i] + (std_dev * std))
                lower_band.append(middle_band[i] - (std_dev * std))
            else:
                upper_band.append(None)
                lower_band.append(None)

        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band
        }
