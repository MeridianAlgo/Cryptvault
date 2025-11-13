"""
Trend Indicators

Moving averages and trend-following indicators implemented with NumPy
vectorization for optimal performance.

Mathematical Formulas:
    SMA(n) = (P1 + P2 + ... + Pn) / n
    EMA(n) = Price(t) × k + EMA(y) × (1 - k), where k = 2/(n+1)
    WMA(n) = (n×P1 + (n-1)×P2 + ... + 1×Pn) / (n×(n+1)/2)

Time Complexity: O(n) for all indicators
Space Complexity: O(n)

Example:
    >>> from cryptvault.indicators.trend import calculate_sma, calculate_ema
    >>> prices = [44.34, 44.09, 43.61, 44.33, 44.83]
    >>> sma = calculate_sma(prices, period=3)
    >>> ema = calculate_ema(prices, period=3)
"""

import numpy as np
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def calculate_sma(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Simple Moving Average.

    SMA is the arithmetic mean of prices over a specified period.

    Formula: SMA = (P1 + P2 + ... + Pn) / n

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with SMA values (NaN for insufficient data)

    Time Complexity: O(n)

    Example:
        >>> prices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> sma = calculate_sma(prices, period=3)
        >>> print(sma[-1])  # Last SMA value
        9.0
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period:
        return np.full(len(prices), np.nan)

    # Use convolution for efficient calculation
    weights = np.ones(period) / period
    sma = np.convolve(prices, weights, mode='valid')

    # Pad with NaN for initial values
    result = np.full(len(prices), np.nan)
    result[period-1:] = sma

    return result


def calculate_ema(
    prices: Union[List[float], np.ndarray],
    period: int = 12
) -> np.ndarray:
    """
    Calculate Exponential Moving Average.

    EMA gives more weight to recent prices using exponential decay.

    Formula: EMA(t) = Price(t) × k + EMA(t-1) × (1 - k)
    where k = 2 / (period + 1)

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with EMA values

    Time Complexity: O(n)

    Example:
        >>> prices = [22.27, 22.19, 22.08, 22.17, 22.18]
        >>> ema = calculate_ema(prices, period=3)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period:
        return np.full(len(prices), np.nan)

    # Calculate multiplier
    multiplier = 2.0 / (period + 1)

    # Initialize with SMA
    ema = np.full(len(prices), np.nan)
    ema[period-1] = np.mean(prices[:period])

    # Calculate EMA iteratively
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]

    return ema


def calculate_wma(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Weighted Moving Average.

    WMA assigns linearly increasing weights to more recent prices.

    Formula: WMA = (n×P1 + (n-1)×P2 + ... + 1×Pn) / (n×(n+1)/2)

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with WMA values

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period:
        return np.full(len(prices), np.nan)

    # Create weights (1, 2, 3, ..., period)
    weights = np.arange(1, period + 1)
    weight_sum = weights.sum()

    wma = np.full(len(prices), np.nan)

    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1:i + 1]
        wma[i] = np.dot(window, weights) / weight_sum

    return wma


def calculate_dema(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Double Exponential Moving Average.

    DEMA reduces lag by using double smoothing.

    Formula: DEMA = 2×EMA - EMA(EMA)

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with DEMA values

    Time Complexity: O(n)
    """
    ema1 = calculate_ema(prices, period)
    ema2 = calculate_ema(ema1[~np.isnan(ema1)], period)

    # Align arrays
    dema = np.full(len(prices), np.nan)
    valid_start = period * 2 - 2

    if len(ema2) > 0 and valid_start < len(prices):
        dema[valid_start:valid_start + len(ema2)] = 2 * ema1[valid_start:valid_start + len(ema2)] - ema2

    return dema


def calculate_tema(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Triple Exponential Moving Average.

    TEMA further reduces lag using triple smoothing.

    Formula: TEMA = 3×EMA - 3×EMA(EMA) + EMA(EMA(EMA))

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with TEMA values

    Time Complexity: O(n)
    """
    ema1 = calculate_ema(prices, period)
    ema2 = calculate_ema(ema1[~np.isnan(ema1)], period)
    ema3 = calculate_ema(ema2[~np.isnan(ema2)], period)

    # Align arrays
    tema = np.full(len(prices), np.nan)
    valid_start = period * 3 - 3

    if len(ema3) > 0 and valid_start < len(prices):
        tema[valid_start:valid_start + len(ema3)] = (
            3 * ema1[valid_start:valid_start + len(ema3)] -
            3 * ema2[valid_start:valid_start + len(ema3)] +
            ema3
        )

    return tema


def calculate_smma(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Smoothed Moving Average (also known as SMMA or RMA).

    SMMA is similar to EMA but with different smoothing factor.

    Formula: SMMA(t) = (SMMA(t-1) × (n-1) + Price(t)) / n

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with SMMA values

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period:
        return np.full(len(prices), np.nan)

    smma = np.full(len(prices), np.nan)
    smma[period-1] = np.mean(prices[:period])

    for i in range(period, len(prices)):
        smma[i] = (smma[i-1] * (period - 1) + prices[i]) / period

    return smma


def calculate_hma(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Hull Moving Average.

    HMA reduces lag and improves smoothing using weighted moving averages.

    Formula: HMA = WMA(2×WMA(n/2) - WMA(n)), sqrt(n))

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with HMA values

    Time Complexity: O(n)
    """
    half_period = period // 2
    sqrt_period = int(np.sqrt(period))

    wma_half = calculate_wma(prices, half_period)
    wma_full = calculate_wma(prices, period)

    # Calculate 2×WMA(n/2) - WMA(n)
    raw_hma = 2 * wma_half - wma_full

    # Apply WMA with sqrt(period)
    hma = calculate_wma(raw_hma[~np.isnan(raw_hma)], sqrt_period)

    # Align result
    result = np.full(len(prices), np.nan)
    valid_start = period + sqrt_period - 2
    if valid_start < len(prices):
        result[valid_start:valid_start + len(hma)] = hma

    return result


def calculate_vwma(
    prices: Union[List[float], np.ndarray],
    volumes: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Volume Weighted Moving Average.

    VWMA weights prices by their trading volume.

    Formula: VWMA = Σ(Price × Volume) / Σ(Volume)

    Args:
        prices: Price data
        volumes: Volume data
        period: Number of periods

    Returns:
        NumPy array with VWMA values

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)
    volumes = np.array(volumes, dtype=float)

    if len(prices) != len(volumes):
        raise ValueError("Prices and volumes must have same length")

    if len(prices) < period:
        return np.full(len(prices), np.nan)

    vwma = np.full(len(prices), np.nan)

    for i in range(period - 1, len(prices)):
        price_window = prices[i - period + 1:i + 1]
        volume_window = volumes[i - period + 1:i + 1]

        if volume_window.sum() > 0:
            vwma[i] = np.dot(price_window, volume_window) / volume_window.sum()

    return vwma


def calculate_zlema(
    prices: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Zero Lag Exponential Moving Average.

    ZLEMA attempts to eliminate lag by using price momentum.

    Formula: ZLEMA = EMA(Price + (Price - Price[lag]))
    where lag = (period - 1) / 2

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with ZLEMA values

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)
    lag = (period - 1) // 2

    if len(prices) < lag + 1:
        return np.full(len(prices), np.nan)

    # Calculate de-lagged prices
    delagged = np.full(len(prices), np.nan)
    delagged[lag:] = prices[lag:] + (prices[lag:] - prices[:-lag])

    # Apply EMA to de-lagged prices
    zlema = calculate_ema(delagged[~np.isnan(delagged)], period)

    # Align result
    result = np.full(len(prices), np.nan)
    result[lag + period - 1:lag + period - 1 + len(zlema)] = zlema

    return result
