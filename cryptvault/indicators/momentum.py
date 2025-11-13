"""
Momentum Indicators

Oscillators and momentum indicators for identifying overbought/oversold
conditions and trend strength.

Mathematical Formulas:
    RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss
    MACD = EMA(12) - EMA(26)
    Signal = EMA(9) of MACD
    Stochastic %K = 100 × (Close - Low(n)) / (High(n) - Low(n))

Time Complexity: O(n) for all indicators

Example:
    >>> from cryptvault.indicators.momentum import calculate_rsi, calculate_macd
    >>> prices = [44.34, 44.09, 43.61, 44.33, 44.83]
    >>> rsi = calculate_rsi(prices, period=14)
    >>> macd_data = calculate_macd(prices)
"""

import numpy as np
from typing import List, Union, Dict, Tuple
import logging

from .trend import calculate_ema, calculate_sma

logger = logging.getLogger(__name__)


def calculate_rsi(
    prices: Union[List[float], np.ndarray],
    period: int = 14
) -> np.ndarray:
    """
    Calculate Relative Strength Index.

    RSI measures momentum by comparing upward and downward price movements.
    Values range from 0 to 100, with >70 indicating overbought and <30 oversold.

    Formula:
        RS = Average Gain / Average Loss
        RSI = 100 - (100 / (1 + RS))

    Args:
        prices: Price data
        period: Number of periods (typically 14)

    Returns:
        NumPy array with RSI values (0-100)

    Time Complexity: O(n)

    Example:
        >>> prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83]
        >>> rsi = calculate_rsi(prices, period=14)
        >>> print(f"RSI: {rsi[-1]:.2f}")
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period + 1:
        return np.full(len(prices), np.nan)

    # Calculate price changes
    deltas = np.diff(prices)

    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    # Calculate initial averages
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    # Initialize RSI array
    rsi = np.full(len(prices), np.nan)

    # Calculate RSI for each period
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i + 1] = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def calculate_macd(
    prices: Union[List[float], np.ndarray],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, np.ndarray]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    MACD shows relationship between two moving averages and is used to
    identify trend changes and momentum.

    Formula:
        MACD Line = EMA(fast) - EMA(slow)
        Signal Line = EMA(signal) of MACD Line
        Histogram = MACD Line - Signal Line

    Args:
        prices: Price data
        fast_period: Fast EMA period (typically 12)
        slow_period: Slow EMA period (typically 26)
        signal_period: Signal line period (typically 9)

    Returns:
        Dictionary with 'macd', 'signal', and 'histogram' arrays

    Time Complexity: O(n)

    Example:
        >>> macd_data = calculate_macd(prices)
        >>> print(f"MACD: {macd_data['macd'][-1]:.2f}")
        >>> print(f"Signal: {macd_data['signal'][-1]:.2f}")
    """
    prices = np.array(prices, dtype=float)

    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line
    valid_macd = macd_line[~np.isnan(macd_line)]
    signal_line_values = calculate_ema(valid_macd, signal_period)

    # Align signal line with original data
    signal_line = np.full(len(prices), np.nan)
    start_idx = slow_period - 1 + signal_period - 1
    if start_idx < len(prices) and len(signal_line_values) > 0:
        end_idx = min(start_idx + len(signal_line_values), len(prices))
        signal_line[start_idx:end_idx] = signal_line_values[:end_idx - start_idx]

    # Calculate histogram
    histogram = macd_line - signal_line

    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_stochastic(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    k_period: int = 14,
    d_period: int = 3
) -> Dict[str, np.ndarray]:
    """
    Calculate Stochastic Oscillator.

    Stochastic compares closing price to price range over a period.
    Values range from 0 to 100, with >80 overbought and <20 oversold.

    Formula:
        %K = 100 × (Close - Low(n)) / (High(n) - Low(n))
        %D = SMA(%K, d_period)

    Args:
        highs: High prices
        lows: Low prices
        closes: Closing prices
        k_period: %K period (typically 14)
        d_period: %D period (typically 3)

    Returns:
        Dictionary with 'k' and 'd' arrays

    Time Complexity: O(n)
    """
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)

    if len(highs) != len(lows) or len(highs) != len(closes):
        raise ValueError("Highs, lows, and closes must have same length")

    if len(closes) < k_period:
        return {
            'k': np.full(len(closes), np.nan),
            'd': np.full(len(closes), np.nan)
        }

    # Calculate %K
    k = np.full(len(closes), np.nan)

    for i in range(k_period - 1, len(closes)):
        high_max = np.max(highs[i - k_period + 1:i + 1])
        low_min = np.min(lows[i - k_period + 1:i + 1])

        if high_max - low_min != 0:
            k[i] = 100.0 * (closes[i] - low_min) / (high_max - low_min)
        else:
            k[i] = 50.0

    # Calculate %D (SMA of %K)
    d = calculate_sma(k[~np.isnan(k)], d_period)

    # Align %D
    d_aligned = np.full(len(closes), np.nan)
    start_idx = k_period - 1 + d_period - 1
    if start_idx < len(closes):
        d_aligned[start_idx:start_idx + len(d)] = d

    return {'k': k, 'd': d_aligned}


def calculate_roc(
    prices: Union[List[float], np.ndarray],
    period: int = 12
) -> np.ndarray:
    """
    Calculate Rate of Change.

    ROC measures percentage change in price over a period.

    Formula: ROC = ((Price(t) - Price(t-n)) / Price(t-n)) × 100

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with ROC values (percentage)

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period + 1:
        return np.full(len(prices), np.nan)

    roc = np.full(len(prices), np.nan)

    for i in range(period, len(prices)):
        if prices[i - period] != 0:
            roc[i] = ((prices[i] - prices[i - period]) / prices[i - period]) * 100.0

    return roc


def calculate_cci(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    period: int = 20
) -> np.ndarray:
    """
    Calculate Commodity Channel Index.

    CCI identifies cyclical trends and overbought/oversold conditions.

    Formula:
        Typical Price = (High + Low + Close) / 3
        CCI = (Typical Price - SMA(Typical Price)) / (0.015 × Mean Deviation)

    Args:
        highs: High prices
        lows: Low prices
        closes: Closing prices
        period: Number of periods (typically 20)

    Returns:
        NumPy array with CCI values

    Time Complexity: O(n)
    """
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)

    # Calculate typical price
    typical_price = (highs + lows + closes) / 3.0

    if len(typical_price) < period:
        return np.full(len(typical_price), np.nan)

    # Calculate SMA of typical price
    sma_tp = calculate_sma(typical_price, period)

    # Calculate mean deviation
    cci = np.full(len(typical_price), np.nan)

    for i in range(period - 1, len(typical_price)):
        window = typical_price[i - period + 1:i + 1]
        mean_dev = np.mean(np.abs(window - sma_tp[i]))

        if mean_dev != 0:
            cci[i] = (typical_price[i] - sma_tp[i]) / (0.015 * mean_dev)

    return cci


def calculate_williams_r(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    period: int = 14
) -> np.ndarray:
    """
    Calculate Williams %R.

    Williams %R is a momentum indicator showing overbought/oversold levels.
    Values range from -100 to 0, with >-20 overbought and <-80 oversold.

    Formula: %R = -100 × (High(n) - Close) / (High(n) - Low(n))

    Args:
        highs: High prices
        lows: Low prices
        closes: Closing prices
        period: Number of periods (typically 14)

    Returns:
        NumPy array with Williams %R values (-100 to 0)

    Time Complexity: O(n)
    """
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)

    if len(closes) < period:
        return np.full(len(closes), np.nan)

    williams_r = np.full(len(closes), np.nan)

    for i in range(period - 1, len(closes)):
        high_max = np.max(highs[i - period + 1:i + 1])
        low_min = np.min(lows[i - period + 1:i + 1])

        if high_max - low_min != 0:
            williams_r[i] = -100.0 * (high_max - closes[i]) / (high_max - low_min)
        else:
            williams_r[i] = -50.0

    return williams_r


def calculate_momentum(
    prices: Union[List[float], np.ndarray],
    period: int = 10
) -> np.ndarray:
    """
    Calculate Momentum indicator.

    Momentum measures the rate of price change.

    Formula: Momentum = Price(t) - Price(t-n)

    Args:
        prices: Price data
        period: Number of periods

    Returns:
        NumPy array with momentum values

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period + 1:
        return np.full(len(prices), np.nan)

    momentum = np.full(len(prices), np.nan)
    momentum[period:] = prices[period:] - prices[:-period]

    return momentum


def calculate_tsi(
    prices: Union[List[float], np.ndarray],
    long_period: int = 25,
    short_period: int = 13
) -> np.ndarray:
    """
    Calculate True Strength Index.

    TSI uses double-smoothed momentum for trend identification.

    Formula:
        Momentum = Price(t) - Price(t-1)
        TSI = 100 × EMA(EMA(Momentum, long), short) / EMA(EMA(|Momentum|, long), short)

    Args:
        prices: Price data
        long_period: Long EMA period (typically 25)
        short_period: Short EMA period (typically 13)

    Returns:
        NumPy array with TSI values

    Time Complexity: O(n)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < 2:
        return np.full(len(prices), np.nan)

    # Calculate momentum
    momentum = np.diff(prices)
    abs_momentum = np.abs(momentum)

    # Double smooth momentum
    ema1 = calculate_ema(momentum, long_period)
    ema1_valid = ema1[~np.isnan(ema1)]
    ema2 = calculate_ema(ema1_valid, short_period)

    # Double smooth absolute momentum
    abs_ema1 = calculate_ema(abs_momentum, long_period)
    abs_ema1_valid = abs_ema1[~np.isnan(abs_ema1)]
    abs_ema2 = calculate_ema(abs_ema1_valid, short_period)

    # Calculate TSI
    tsi = np.full(len(prices), np.nan)

    if len(ema2) > 0 and len(abs_ema2) > 0:
        min_len = min(len(ema2), len(abs_ema2))
        tsi_values = np.where(
            abs_ema2[:min_len] != 0,
            100.0 * ema2[:min_len] / abs_ema2[:min_len],
            0.0
        )

        start_idx = long_period + short_period - 1
        if start_idx < len(prices):
            tsi[start_idx:start_idx + len(tsi_values)] = tsi_values

    return tsi
