"""Moving average calculations for technical analysis."""

from typing import List, Optional
import math
from ..data.models import PriceDataFrame


class MovingAverages:
    """Calculate various types of moving averages."""
    
    def __init__(self):
        """Initialize moving averages calculator."""
        pass
    
    def simple_moving_average(self, values: List[float], period: int) -> List[Optional[float]]:
        """
        Calculate Simple Moving Average (SMA).
        
        Args:
            values: List of values to calculate SMA for
            period: Number of periods for the moving average
            
        Returns:
            List of SMA values with None for insufficient data points
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if len(values) < period:
            return [None] * len(values)
        
        sma_values = []
        
        for i in range(len(values)):
            if i < period - 1:
                sma_values.append(None)
            else:
                window = values[i - period + 1:i + 1]
                sma = sum(window) / period
                sma_values.append(sma)
        
        return sma_values
    
    def exponential_moving_average(self, values: List[float], period: int) -> List[Optional[float]]:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            values: List of values to calculate EMA for
            period: Number of periods for the moving average
            
        Returns:
            List of EMA values with None for insufficient data points
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if len(values) < period:
            return [None] * len(values)
        
        ema_values = [None] * (period - 1)
        
        # Calculate initial SMA for first EMA value
        initial_sma = sum(values[:period]) / period
        ema_values.append(initial_sma)
        
        # Calculate multiplier
        multiplier = 2 / (period + 1)
        
        # Calculate subsequent EMA values
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def weighted_moving_average(self, values: List[float], period: int) -> List[Optional[float]]:
        """
        Calculate Weighted Moving Average (WMA).
        More recent values have higher weights.
        
        Args:
            values: List of values to calculate WMA for
            period: Number of periods for the moving average
            
        Returns:
            List of WMA values with None for insufficient data points
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if len(values) < period:
            return [None] * len(values)
        
        wma_values = []
        
        # Calculate weight sum (1 + 2 + ... + period)
        weight_sum = period * (period + 1) / 2
        
        for i in range(len(values)):
            if i < period - 1:
                wma_values.append(None)
            else:
                window = values[i - period + 1:i + 1]
                
                # Calculate weighted sum
                weighted_sum = 0
                for j, value in enumerate(window):
                    weight = j + 1  # Weights from 1 to period
                    weighted_sum += value * weight
                
                wma = weighted_sum / weight_sum
                wma_values.append(wma)
        
        return wma_values
    
    def hull_moving_average(self, values: List[float], period: int) -> List[Optional[float]]:
        """
        Calculate Hull Moving Average (HMA).
        Reduces lag while maintaining smoothness.
        
        Args:
            values: List of values to calculate HMA for
            period: Number of periods for the moving average
            
        Returns:
            List of HMA values with None for insufficient data points
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if len(values) < period:
            return [None] * len(values)
        
        # Calculate WMA with period/2
        half_period = max(1, period // 2)
        wma_half = self.weighted_moving_average(values, half_period)
        
        # Calculate WMA with full period
        wma_full = self.weighted_moving_average(values, period)
        
        # Calculate 2 * WMA(period/2) - WMA(period)
        raw_hma = []
        for i in range(len(values)):
            if wma_half[i] is not None and wma_full[i] is not None:
                raw_hma.append(2 * wma_half[i] - wma_full[i])
            else:
                raw_hma.append(None)
        
        # Apply WMA with sqrt(period) to the result
        sqrt_period = max(1, int(math.sqrt(period)))
        
        # Filter out None values for final WMA calculation
        valid_indices = [i for i, val in enumerate(raw_hma) if val is not None]
        if len(valid_indices) < sqrt_period:
            return [None] * len(values)
        
        hma_values = [None] * len(values)
        
        # Calculate final HMA
        for i in range(len(valid_indices)):
            if i < sqrt_period - 1:
                continue
            
            # Get window of valid raw HMA values
            window_indices = valid_indices[i - sqrt_period + 1:i + 1]
            window_values = [raw_hma[idx] for idx in window_indices]
            
            # Calculate weighted average
            weight_sum = sqrt_period * (sqrt_period + 1) / 2
            weighted_sum = sum(val * (j + 1) for j, val in enumerate(window_values))
            hma = weighted_sum / weight_sum
            
            # Place result at the correct index
            result_index = valid_indices[i]
            hma_values[result_index] = hma
        
        return hma_values
    
    def adaptive_moving_average(self, values: List[float], period: int, 
                              fast_sc: float = 2.0, slow_sc: float = 30.0) -> List[Optional[float]]:
        """
        Calculate Adaptive Moving Average (AMA) - Kaufman's Adaptive Moving Average.
        Adjusts smoothing based on market volatility.
        
        Args:
            values: List of values to calculate AMA for
            period: Number of periods for efficiency ratio calculation
            fast_sc: Fast smoothing constant (default 2.0)
            slow_sc: Slow smoothing constant (default 30.0)
            
        Returns:
            List of AMA values with None for insufficient data points
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if len(values) < period + 1:
            return [None] * len(values)
        
        ama_values = [None] * period
        
        # Initialize first AMA value as the first available price
        ama_values.append(values[period])
        
        # Calculate smoothing constants
        fast_sc_ratio = 2 / (fast_sc + 1)
        slow_sc_ratio = 2 / (slow_sc + 1)
        
        for i in range(period + 1, len(values)):
            # Calculate direction (change over period)
            direction = abs(values[i] - values[i - period])
            
            # Calculate volatility (sum of absolute changes)
            volatility = sum(abs(values[j] - values[j - 1]) 
                           for j in range(i - period + 1, i + 1))
            
            # Calculate efficiency ratio
            if volatility == 0:
                efficiency_ratio = 1.0
            else:
                efficiency_ratio = direction / volatility
            
            # Calculate smoothing constant
            sc = (efficiency_ratio * (fast_sc_ratio - slow_sc_ratio) + slow_sc_ratio) ** 2
            
            # Calculate AMA
            ama = ama_values[-1] + sc * (values[i] - ama_values[-1])
            ama_values.append(ama)
        
        return ama_values
    
    def triangular_moving_average(self, values: List[float], period: int) -> List[Optional[float]]:
        """
        Calculate Triangular Moving Average (TMA).
        Double-smoothed moving average.
        
        Args:
            values: List of values to calculate TMA for
            period: Number of periods for the moving average
            
        Returns:
            List of TMA values with None for insufficient data points
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        # First, calculate SMA
        first_sma = self.simple_moving_average(values, period)
        
        # Then calculate SMA of the SMA
        # Filter out None values for second SMA calculation
        valid_sma = [val for val in first_sma if val is not None]
        
        if len(valid_sma) < period:
            return [None] * len(values)
        
        second_sma = self.simple_moving_average(valid_sma, period)
        
        # Align the result with original data length
        tma_values = [None] * len(values)
        
        # Find where first SMA starts having values
        first_valid_idx = next(i for i, val in enumerate(first_sma) if val is not None)
        
        # Place second SMA values at appropriate positions
        for i, val in enumerate(second_sma):
            if val is not None:
                result_idx = first_valid_idx + period - 1 + i
                if result_idx < len(tma_values):
                    tma_values[result_idx] = val
        
        return tma_values
    
    def get_ma_crossover_signals(self, fast_ma: List[Optional[float]], 
                                slow_ma: List[Optional[float]]) -> List[Optional[str]]:
        """
        Detect moving average crossover signals.
        
        Args:
            fast_ma: Fast moving average values
            slow_ma: Slow moving average values
            
        Returns:
            List of signals: 'bullish_cross', 'bearish_cross', or None
        """
        if len(fast_ma) != len(slow_ma):
            raise ValueError("Moving average lists must have the same length")
        
        signals = [None]  # First value can't have a crossover
        
        for i in range(1, len(fast_ma)):
            current_fast = fast_ma[i]
            current_slow = slow_ma[i]
            prev_fast = fast_ma[i-1]
            prev_slow = slow_ma[i-1]
            
            # Check if we have valid values for comparison
            if all(val is not None for val in [current_fast, current_slow, prev_fast, prev_slow]):
                # Bullish crossover: fast MA crosses above slow MA
                if prev_fast <= prev_slow and current_fast > current_slow:
                    signals.append('bullish_cross')
                # Bearish crossover: fast MA crosses below slow MA
                elif prev_fast >= prev_slow and current_fast < current_slow:
                    signals.append('bearish_cross')
                else:
                    signals.append(None)
            else:
                signals.append(None)
        
        return signals