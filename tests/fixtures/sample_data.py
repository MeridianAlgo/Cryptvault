"""
Sample data fixtures for testing.

Provides various price data scenarios for pattern detection testing.
"""

from datetime import datetime, timedelta
from typing import List
import numpy as np

from cryptvault.data.models import PricePoint, PriceDataFrame


def create_triangle_pattern_data() -> PriceDataFrame:
    """
    Create price data with ascending triangle pattern.
    
    Returns:
        PriceDataFrame with ascending triangle pattern
    """
    base_time = datetime(2024, 1, 1)
    points = []
    
    # Create ascending triangle: higher lows, flat resistance
    resistance = 52000.0
    
    for i in range(30):
        # Higher lows
        low = 48000 + (i * 100)
        # Flat resistance with some noise
        high = resistance + np.random.uniform(-100, 100)
        
        open_price = low + np.random.uniform(0, high - low) * 0.3
        close = low + np.random.uniform(0, high - low) * 0.7
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=1000000.0
        )
        points.append(point)
    
    return PriceDataFrame(points, symbol='TEST', interval='1d')


def create_head_and_shoulders_data() -> PriceDataFrame:
    """
    Create price data with head and shoulders pattern.
    
    Returns:
        PriceDataFrame with head and shoulders pattern
    """
    base_time = datetime(2024, 1, 1)
    base_price = 50000.0
    points = []
    
    # Pattern: left shoulder, head, right shoulder
    pattern_prices = [
        # Left shoulder
        50000, 51000, 52000, 51000, 50000,
        # Head
        51000, 52000, 53000, 54000, 53000, 52000, 51000,
        # Right shoulder
        52000, 53000, 52000, 51000, 50000,
        # Breakdown
        49000, 48000, 47000
    ]
    
    for i, close in enumerate(pattern_prices):
        open_price = close + np.random.uniform(-200, 200)
        high = max(open_price, close) + abs(np.random.uniform(0, 300))
        low = min(open_price, close) - abs(np.random.uniform(0, 300))
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=1000000.0
        )
        points.append(point)
    
    return PriceDataFrame(points, symbol='TEST', interval='1d')


def create_double_bottom_data() -> PriceDataFrame:
    """
    Create price data with double bottom pattern.
    
    Returns:
        PriceDataFrame with double bottom pattern
    """
    base_time = datetime(2024, 1, 1)
    points = []
    
    # Pattern: decline, first bottom, rally, second bottom, breakout
    pattern_prices = [
        # Decline to first bottom
        52000, 51000, 50000, 49000, 48000,
        # Rally
        49000, 50000, 51000, 50000,
        # Decline to second bottom
        49000, 48000, 48100,
        # Breakout
        49000, 50000, 51000, 52000, 53000
    ]
    
    for i, close in enumerate(pattern_prices):
        open_price = close + np.random.uniform(-100, 100)
        high = max(open_price, close) + abs(np.random.uniform(0, 200))
        low = min(open_price, close) - abs(np.random.uniform(0, 200))
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=1000000.0
        )
        points.append(point)
    
    return PriceDataFrame(points, symbol='TEST', interval='1d')


def create_bull_flag_data() -> PriceDataFrame:
    """
    Create price data with bull flag pattern.
    
    Returns:
        PriceDataFrame with bull flag pattern
    """
    base_time = datetime(2024, 1, 1)
    points = []
    
    # Strong uptrend (flagpole)
    for i in range(10):
        close = 45000 + (i * 500)
        open_price = close - 100
        high = close + 200
        low = open_price - 100
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=2000000.0
        )
        points.append(point)
    
    # Consolidation (flag)
    flag_high = points[-1].close
    for i in range(10, 20):
        close = flag_high - ((i - 10) * 50)
        open_price = close + 50
        high = open_price + 100
        low = close - 50
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=1000000.0
        )
        points.append(point)
    
    # Breakout
    for i in range(20, 25):
        close = points[-1].close + 500
        open_price = close - 100
        high = close + 200
        low = open_price - 100
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=2500000.0
        )
        points.append(point)
    
    return PriceDataFrame(points, symbol='TEST', interval='1d')


def create_rsi_divergence_data() -> PriceDataFrame:
    """
    Create price data showing RSI divergence.
    
    Returns:
        PriceDataFrame with bullish RSI divergence
    """
    base_time = datetime(2024, 1, 1)
    points = []
    
    # Price makes lower lows, but RSI will make higher lows (bullish divergence)
    pattern_prices = [
        50000, 49000, 48000, 49000, 50000,  # First low
        49000, 48000, 47000, 48000, 49000,  # Second low (lower)
        47000, 46000, 45000, 46000, 47000,  # Third low (even lower)
        48000, 50000, 52000, 54000, 56000   # Reversal
    ]
    
    for i, close in enumerate(pattern_prices):
        open_price = close + np.random.uniform(-200, 200)
        high = max(open_price, close) + abs(np.random.uniform(0, 300))
        low = min(open_price, close) - abs(np.random.uniform(0, 300))
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=1000000.0
        )
        points.append(point)
    
    return PriceDataFrame(points, symbol='TEST', interval='1d')
