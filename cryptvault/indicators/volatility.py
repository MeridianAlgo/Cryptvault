"""
Volatility Indicators

Indicators measuring price volatility and range for risk assessment.

Example:
    >>> from cryptvault.indicators.volatility import calculate_bollinger_bands, calculate_atr
    >>> bb = calculate_bollinger_bands(prices)
    >>> atr = calculate_atr(highs, lows, closes)
"""

import numpy as np
from typing import List, Union, Dict
from .trend import calculate_sma, calculate_ema

def calculate_bollinger_bands(
    prices: Union[List[float], np.ndarray],
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, np.ndarray]:
    """Calculate Bollinger Bands."""
    prices = np.array(prices, dtype=float)
    middle = calculate_sma(prices, period)

    std = np.full(len(prices), np.nan)
    for i in range(period - 1, len(prices)):
        std[i] = np.std(prices[i - period + 1:i + 1])

    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)

    return {'upper': upper, 'middle': middle, 'lower': lower}


def calculate_atr(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    period: int = 14
) -> np.ndarray:
    """Calculate Average True Range."""
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)

    tr = np.full(len(closes), np.nan)
    tr[0] = highs[0] - lows[0]

    for i in range(1, len(closes)):
        tr[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )

    atr = calculate_sma(tr, period)
    return atr


def calculate_keltner_channels(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    period: int = 20,
    multiplier: float = 2.0
) -> Dict[str, np.ndarray]:
    """Calculate Keltner Channels."""
    closes = np.array(closes, dtype=float)
    middle = calculate_ema(closes, period)
    atr = calculate_atr(highs, lows, closes, period)

    upper = middle + (multiplier * atr)
    lower = middle - (multiplier * atr)

    return {'upper': upper, 'middle': middle, 'lower': lower}
