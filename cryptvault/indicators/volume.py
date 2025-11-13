"""
Volume Indicators

Volume-based indicators for analyzing trading activity.

Example:
    >>> from cryptvault.indicators.volume import calculate_obv, calculate_vwap
    >>> obv = calculate_obv(closes, volumes)
    >>> vwap = calculate_vwap(highs, lows, closes, volumes)
"""

import numpy as np
from typing import List, Union
from .trend import calculate_sma

def calculate_obv(
    closes: Union[List[float], np.ndarray],
    volumes: Union[List[float], np.ndarray]
) -> np.ndarray:
    """Calculate On-Balance Volume."""
    closes = np.array(closes, dtype=float)
    volumes = np.array(volumes, dtype=float)

    obv = np.zeros(len(closes))
    obv[0] = volumes[0]

    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv[i] = obv[i-1] + volumes[i]
        elif closes[i] < closes[i-1]:
            obv[i] = obv[i-1] - volumes[i]
        else:
            obv[i] = obv[i-1]

    return obv


def calculate_vwap(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    volumes: Union[List[float], np.ndarray]
) -> np.ndarray:
    """Calculate Volume Weighted Average Price."""
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)
    volumes = np.array(volumes, dtype=float)

    typical_price = (highs + lows + closes) / 3.0
    vwap = np.cumsum(typical_price * volumes) / np.cumsum(volumes)

    return vwap


def calculate_mfi(
    highs: Union[List[float], np.ndarray],
    lows: Union[List[float], np.ndarray],
    closes: Union[List[float], np.ndarray],
    volumes: Union[List[float], np.ndarray],
    period: int = 14
) -> np.ndarray:
    """Calculate Money Flow Index."""
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)
    volumes = np.array(volumes, dtype=float)

    typical_price = (highs + lows + closes) / 3.0
    money_flow = typical_price * volumes

    mfi = np.full(len(closes), np.nan)

    for i in range(period, len(closes)):
        positive_flow = 0
        negative_flow = 0

        for j in range(i - period + 1, i + 1):
            if j > 0:
                if typical_price[j] > typical_price[j-1]:
                    positive_flow += money_flow[j]
                elif typical_price[j] < typical_price[j-1]:
                    negative_flow += money_flow[j]

        if negative_flow == 0:
            mfi[i] = 100.0
        else:
            money_ratio = positive_flow / negative_flow
            mfi[i] = 100.0 - (100.0 / (1.0 + money_ratio))

    return mfi
