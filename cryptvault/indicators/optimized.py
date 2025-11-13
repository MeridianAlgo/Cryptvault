"""
Optimized Indicator Calculations

This module provides optimized versions of technical indicators with:
- Aggressive caching to avoid redundant calculations
- Vectorized NumPy operations for maximum performance
- Batch calculation support
- Memory-efficient implementations

All functions maintain O(n) time complexity but with reduced constants.

Example:
    >>> from cryptvault.indicators.optimized import OptimizedIndicators
    >>> calc = OptimizedIndicators()
    >>> indicators = calc.calculate_all(data)
"""

import numpy as np
from typing import Dict, List, Union, Optional
import logging

from .trend import calculate_sma, calculate_ema
from .momentum import calculate_rsi, calculate_macd
from .volatility import calculate_bollinger_bands, calculate_atr
from ..utils.calculation_cache import cached_calculation, BatchCalculator
from ..data.models import PriceDataFrame

logger = logging.getLogger(__name__)


class OptimizedIndicators:
    """
    Optimized technical indicator calculator with caching.

    This class provides efficient calculation of multiple indicators
    with automatic caching and batch processing capabilities.

    Example:
        >>> calc = OptimizedIndicators()
        >>> indicators = calc.calculate_all(price_data)
        >>> print(f"RSI: {indicators['rsi'][-1]:.2f}")
    """

    def __init__(self, enable_cache: bool = True):
        """
        Initialize optimized indicator calculator.

        Args:
            enable_cache: Whether to enable result caching (default: True)
        """
        self.enable_cache = enable_cache
        self.batch_calculator = BatchCalculator()

    @cached_calculation(ttl=300)
    def calculate_all(self, data: PriceDataFrame) -> Dict[str, np.ndarray]:
        """
        Calculate all common indicators efficiently.

        This method calculates multiple indicators in a single pass,
        reusing intermediate calculations where possible.

        Args:
            data: Price data frame

        Returns:
            Dictionary with all calculated indicators

        Time Complexity: O(n) - single pass through data
        """
        closes = np.array(data.get_closes())
        highs = np.array(data.get_highs())
        lows = np.array(data.get_lows())
        volumes = np.array(data.get_volumes())

        indicators = {}

        # Calculate EMAs (reused by other indicators)
        ema_12 = calculate_ema(closes, 12)
        ema_26 = calculate_ema(closes, 26)

        indicators['ema_12'] = ema_12
        indicators['ema_26'] = ema_26

        # MACD (reuses EMAs)
        macd_line = ema_12 - ema_26
        signal_line_values = calculate_ema(macd_line[~np.isnan(macd_line)], 9)

        signal_line = np.full(len(closes), np.nan)
        start_idx = 26 - 1 + 9 - 1
        if start_idx < len(closes):
            signal_line[start_idx:start_idx + len(signal_line_values)] = signal_line_values

        indicators['macd'] = macd_line
        indicators['macd_signal'] = signal_line
        indicators['macd_histogram'] = macd_line - signal_line

        # SMAs
        indicators['sma_20'] = calculate_sma(closes, 20)
        indicators['sma_50'] = calculate_sma(closes, 50)
        indicators['sma_200'] = calculate_sma(closes, 200)

        # RSI
        indicators['rsi'] = calculate_rsi(closes, 14)

        # Bollinger Bands
        bb = calculate_bollinger_bands(closes, period=20, std_dev=2.0)
        indicators['bb_upper'] = bb['upper']
        indicators['bb_middle'] = bb['middle']
        indicators['bb_lower'] = bb['lower']

        # ATR
        indicators['atr'] = calculate_atr(highs, lows, closes, period=14)

        # Volume SMA
        indicators['volume_sma'] = calculate_sma(volumes, 20)

        logger.debug(f"Calculated {len(indicators)} indicators for {len(closes)} data points")

        return indicators

    @cached_calculation(ttl=300)
    def calculate_trend_indicators(self, closes: Union[List[float], np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calculate only trend indicators efficiently.

        Args:
            closes: Closing prices

        Returns:
            Dictionary with trend indicators
        """
        closes = np.array(closes, dtype=float)

        return {
            'sma_20': calculate_sma(closes, 20),
            'sma_50': calculate_sma(closes, 50),
            'sma_200': calculate_sma(closes, 200),
            'ema_12': calculate_ema(closes, 12),
            'ema_26': calculate_ema(closes, 26),
            'ema_50': calculate_ema(closes, 50)
        }

    @cached_calculation(ttl=300)
    def calculate_momentum_indicators(self, closes: Union[List[float], np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calculate only momentum indicators efficiently.

        Args:
            closes: Closing prices

        Returns:
            Dictionary with momentum indicators
        """
        closes = np.array(closes, dtype=float)

        # Calculate RSI
        rsi = calculate_rsi(closes, 14)

        # Calculate MACD
        macd_data = calculate_macd(closes)

        return {
            'rsi': rsi,
            'macd': macd_data['macd'],
            'macd_signal': macd_data['signal'],
            'macd_histogram': macd_data['histogram']
        }

    def calculate_batch(self, data_frames: List[PriceDataFrame]) -> List[Dict[str, np.ndarray]]:
        """
        Calculate indicators for multiple data frames efficiently.

        This method processes multiple data frames in batch, potentially
        reusing calculations and reducing overhead.

        Args:
            data_frames: List of price data frames

        Returns:
            List of indicator dictionaries
        """
        results = []

        for data_frame in data_frames:
            indicators = self.calculate_all(data_frame)
            results.append(indicators)

        return results

    def clear_cache(self) -> None:
        """Clear all cached calculations."""
        if hasattr(self.calculate_all, 'clear_cache'):
            self.calculate_all.clear_cache()
        if hasattr(self.calculate_trend_indicators, 'clear_cache'):
            self.calculate_trend_indicators.clear_cache()
        if hasattr(self.calculate_momentum_indicators, 'clear_cache'):
            self.calculate_momentum_indicators.clear_cache()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        stats = {}

        if hasattr(self.calculate_all, 'get_cache_stats'):
            stats['calculate_all'] = self.calculate_all.get_cache_stats()
        if hasattr(self.calculate_trend_indicators, 'get_cache_stats'):
            stats['trend_indicators'] = self.calculate_trend_indicators.get_cache_stats()
        if hasattr(self.calculate_momentum_indicators, 'get_cache_stats'):
            stats['momentum_indicators'] = self.calculate_momentum_indicators.get_cache_stats()

        return stats


def calculate_indicators_vectorized(
    closes: np.ndarray,
    highs: Optional[np.ndarray] = None,
    lows: Optional[np.ndarray] = None,
    volumes: Optional[np.ndarray] = None
) -> Dict[str, np.ndarray]:
    """
    Calculate multiple indicators in a single vectorized pass.

    This function is optimized for maximum performance by:
    - Using pure NumPy operations
    - Minimizing array allocations
    - Reusing intermediate calculations
    - Avoiding Python loops where possible

    Args:
        closes: Closing prices
        highs: High prices (optional)
        lows: Low prices (optional)
        volumes: Volume data (optional)

    Returns:
        Dictionary with calculated indicators

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    n = len(closes)
    indicators = {}

    # Pre-allocate arrays for efficiency
    sma_20 = np.full(n, np.nan)
    ema_12 = np.full(n, np.nan)
    ema_26 = np.full(n, np.nan)

    # Calculate SMA 20 using convolution (fastest method)
    if n >= 20:
        weights = np.ones(20) / 20
        sma_values = np.convolve(closes, weights, mode='valid')
        sma_20[19:] = sma_values
    indicators['sma_20'] = sma_20

    # Calculate EMAs efficiently
    if n >= 12:
        multiplier_12 = 2.0 / 13.0
        ema_12[11] = np.mean(closes[:12])
        for i in range(12, n):
            ema_12[i] = (closes[i] - ema_12[i-1]) * multiplier_12 + ema_12[i-1]
    indicators['ema_12'] = ema_12

    if n >= 26:
        multiplier_26 = 2.0 / 27.0
        ema_26[25] = np.mean(closes[:26])
        for i in range(26, n):
            ema_26[i] = (closes[i] - ema_26[i-1]) * multiplier_26 + ema_26[i-1]
    indicators['ema_26'] = ema_26

    # MACD (reuses EMAs)
    indicators['macd'] = ema_12 - ema_26

    # RSI (optimized calculation)
    if n >= 15:
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[:14])
        avg_loss = np.mean(losses[:14])

        rsi = np.full(n, np.nan)
        for i in range(14, len(deltas)):
            avg_gain = (avg_gain * 13 + gains[i]) / 14
            avg_loss = (avg_loss * 13 + losses[i]) / 14

            if avg_loss == 0:
                rsi[i + 1] = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi[i + 1] = 100.0 - (100.0 / (1.0 + rs))

        indicators['rsi'] = rsi

    return indicators


def optimize_calculation_order(required_indicators: List[str]) -> List[str]:
    """
    Optimize the order of indicator calculations to maximize reuse.

    This function analyzes dependencies between indicators and returns
    an optimal calculation order.

    Args:
        required_indicators: List of indicator names to calculate

    Returns:
        Optimized order of calculation

    Example:
        >>> indicators = ['macd', 'ema_12', 'ema_26']
        >>> order = optimize_calculation_order(indicators)
        >>> # Returns: ['ema_12', 'ema_26', 'macd']
    """
    # Define dependencies
    dependencies = {
        'macd': ['ema_12', 'ema_26'],
        'macd_signal': ['macd'],
        'macd_histogram': ['macd', 'macd_signal'],
        'bb_upper': ['sma_20'],
        'bb_middle': ['sma_20'],
        'bb_lower': ['sma_20']
    }

    # Topological sort
    ordered = []
    visited = set()

    def visit(indicator: str):
        if indicator in visited:
            return
        visited.add(indicator)

        # Visit dependencies first
        if indicator in dependencies:
            for dep in dependencies[indicator]:
                if dep in required_indicators:
                    visit(dep)

        ordered.append(indicator)

    for indicator in required_indicators:
        visit(indicator)

    return ordered
