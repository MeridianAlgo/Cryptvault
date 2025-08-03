"""Technical indicators implementation for RSI, MACD, and other indicators."""

from typing import List, Dict, Tuple, Optional
import math
from ..data.models import PriceDataFrame


class TechnicalIndicators:
    """Calculate technical indicators for price data analysis."""
    
    def __init__(self):
        """Initialize technical indicators calculator."""
        pass
    
    def calculate_rsi(self, data: PriceDataFrame, period: int = 14) -> List[float]:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            data: Price data frame
            period: RSI calculation period (default 14)
            
        Returns:
            List of RSI values (0-100)
        """
        closes = data.get_closes()
        
        if len(closes) < period + 1:
            raise ValueError(f"Insufficient data for RSI calculation. Need at least {period + 1} points, got {len(closes)}")
        
        # Calculate price changes
        price_changes = []
        for i in range(1, len(closes)):
            price_changes.append(closes[i] - closes[i-1])
        
        # Separate gains and losses
        gains = [max(change, 0) for change in price_changes]
        losses = [abs(min(change, 0)) for change in price_changes]
        
        rsi_values = []
        
        # Calculate initial average gain and loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate first RSI value
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
        
        # Calculate subsequent RSI values using smoothed averages
        for i in range(period, len(price_changes)):
            # Smoothed average calculation (Wilder's smoothing)
            avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
            avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        # Pad with None values for the initial period
        result = [None] * period + rsi_values
        
        return result
    
    def calculate_macd(self, data: PriceDataFrame, fast_period: int = 12, 
                      slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price data frame
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)
            
        Returns:
            Dictionary with 'macd', 'signal', and 'histogram' lists
        """
        closes = data.get_closes()
        
        if len(closes) < slow_period:
            raise ValueError(f"Insufficient data for MACD calculation. Need at least {slow_period} points, got {len(closes)}")
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(closes, fast_period)
        slow_ema = self._calculate_ema(closes, slow_period)
        
        # Calculate MACD line
        macd_line = []
        for i in range(len(closes)):
            if fast_ema[i] is not None and slow_ema[i] is not None:
                macd_line.append(fast_ema[i] - slow_ema[i])
            else:
                macd_line.append(None)
        
        # Calculate signal line (EMA of MACD line)
        # Filter out None values for signal calculation
        macd_values_for_signal = [val for val in macd_line if val is not None]
        if len(macd_values_for_signal) < signal_period:
            signal_line = [None] * len(closes)
            histogram = [None] * len(closes)
        else:
            signal_ema = self._calculate_ema(macd_values_for_signal, signal_period)
            
            # Align signal line with original data
            signal_line = [None] * len(closes)
            macd_start_idx = next(i for i, val in enumerate(macd_line) if val is not None)
            
            for i, sig_val in enumerate(signal_ema):
                if sig_val is not None and macd_start_idx + i < len(signal_line):
                    signal_line[macd_start_idx + i] = sig_val
            
            # Calculate histogram (MACD - Signal)
            histogram = []
            for i in range(len(closes)):
                if macd_line[i] is not None and signal_line[i] is not None:
                    histogram.append(macd_line[i] - signal_line[i])
                else:
                    histogram.append(None)
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_ema(self, values: List[float], period: int) -> List[float]:
        """
        Calculate Exponential Moving Average.
        
        Args:
            values: List of values
            period: EMA period
            
        Returns:
            List of EMA values
        """
        if len(values) < period:
            return [None] * len(values)
        
        ema_values = [None] * (period - 1)
        
        # Calculate initial SMA for first EMA value
        sma = sum(values[:period]) / period
        ema_values.append(sma)
        
        # Calculate multiplier
        multiplier = 2 / (period + 1)
        
        # Calculate subsequent EMA values
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_bollinger_bands(self, data: PriceDataFrame, period: int = 20, 
                                 std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price data frame
            period: Moving average period (default 20)
            std_dev: Standard deviation multiplier (default 2.0)
            
        Returns:
            Dictionary with 'upper', 'middle', and 'lower' band lists
        """
        closes = data.get_closes()
        
        if len(closes) < period:
            raise ValueError(f"Insufficient data for Bollinger Bands. Need at least {period} points, got {len(closes)}")
        
        upper_band = []
        middle_band = []
        lower_band = []
        
        for i in range(len(closes)):
            if i < period - 1:
                upper_band.append(None)
                middle_band.append(None)
                lower_band.append(None)
            else:
                # Calculate SMA (middle band)
                window = closes[i - period + 1:i + 1]
                sma = sum(window) / period
                
                # Calculate standard deviation
                variance = sum((x - sma) ** 2 for x in window) / period
                std = math.sqrt(variance)
                
                # Calculate bands
                upper = sma + (std_dev * std)
                lower = sma - (std_dev * std)
                
                upper_band.append(upper)
                middle_band.append(sma)
                lower_band.append(lower)
        
        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band
        }
    
    def calculate_stochastic(self, data: PriceDataFrame, k_period: int = 14, 
                           d_period: int = 3) -> Dict[str, List[float]]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            data: Price data frame
            k_period: %K period (default 14)
            d_period: %D period (default 3)
            
        Returns:
            Dictionary with 'k' and 'd' lists
        """
        highs = data.get_highs()
        lows = data.get_lows()
        closes = data.get_closes()
        
        if len(closes) < k_period:
            raise ValueError(f"Insufficient data for Stochastic. Need at least {k_period} points, got {len(closes)}")
        
        k_values = []
        
        for i in range(len(closes)):
            if i < k_period - 1:
                k_values.append(None)
            else:
                # Get highest high and lowest low in the period
                period_highs = highs[i - k_period + 1:i + 1]
                period_lows = lows[i - k_period + 1:i + 1]
                
                highest_high = max(period_highs)
                lowest_low = min(period_lows)
                
                # Calculate %K
                if highest_high == lowest_low:
                    k = 50.0  # Avoid division by zero
                else:
                    k = ((closes[i] - lowest_low) / (highest_high - lowest_low)) * 100
                
                k_values.append(k)
        
        # Calculate %D (SMA of %K)
        d_values = []
        for i in range(len(k_values)):
            if i < k_period - 1 + d_period - 1:
                d_values.append(None)
            else:
                # Get valid %K values for %D calculation
                k_window = [k for k in k_values[i - d_period + 1:i + 1] if k is not None]
                if len(k_window) == d_period:
                    d = sum(k_window) / d_period
                    d_values.append(d)
                else:
                    d_values.append(None)
        
        return {
            'k': k_values,
            'd': d_values
        }
    
    def find_peaks_and_troughs(self, values: List[float], min_distance: int = 5) -> Dict[str, List[int]]:
        """
        Find peaks and troughs in a series of values.
        
        Args:
            values: List of values to analyze
            min_distance: Minimum distance between peaks/troughs
            
        Returns:
            Dictionary with 'peaks' and 'troughs' index lists
        """
        if len(values) < 3:
            return {'peaks': [], 'troughs': []}
        
        peaks = []
        troughs = []
        
        for i in range(1, len(values) - 1):
            if values[i] is None:
                continue
            
            # Check for peak
            if (values[i-1] is not None and values[i+1] is not None and
                values[i] > values[i-1] and values[i] > values[i+1]):
                
                # Check minimum distance from last peak
                if not peaks or i - peaks[-1] >= min_distance:
                    peaks.append(i)
            
            # Check for trough
            if (values[i-1] is not None and values[i+1] is not None and
                values[i] < values[i-1] and values[i] < values[i+1]):
                
                # Check minimum distance from last trough
                if not troughs or i - troughs[-1] >= min_distance:
                    troughs.append(i)
        
        return {'peaks': peaks, 'troughs': troughs}
    
    def calculate_atr(self, data: PriceDataFrame, period: int = 14) -> List[float]:
        """
        Calculate Average True Range (ATR).
        
        Args:
            data: Price data frame
            period: ATR period (default 14)
            
        Returns:
            List of ATR values
        """
        highs = data.get_highs()
        lows = data.get_lows()
        closes = data.get_closes()
        
        if len(closes) < period + 1:
            raise ValueError(f"Insufficient data for ATR. Need at least {period + 1} points, got {len(closes)}")
        
        true_ranges = []
        
        for i in range(1, len(closes)):
            # True Range = max(high-low, |high-prev_close|, |low-prev_close|)
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            
            tr = max(hl, hc, lc)
            true_ranges.append(tr)
        
        atr_values = [None]  # First value is None
        
        # Calculate initial ATR (SMA of first period true ranges)
        initial_atr = sum(true_ranges[:period]) / period
        atr_values.append(initial_atr)
        
        # Calculate subsequent ATR values (smoothed)
        for i in range(period, len(true_ranges)):
            atr = ((atr_values[-1] * (period - 1)) + true_ranges[i]) / period
            atr_values.append(atr)
        
        return atr_values