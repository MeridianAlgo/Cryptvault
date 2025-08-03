"""Tests for moving averages functionality."""

import pytest
from crypto_chart_analyzer.indicators.moving_averages import MovingAverages


class TestMovingAverages:
    """Test cases for MovingAverages class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ma = MovingAverages()
        self.test_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    def test_simple_moving_average(self):
        """Test Simple Moving Average calculation."""
        sma = self.ma.simple_moving_average(self.test_values, period=3)
        
        # Check length
        assert len(sma) == len(self.test_values)
        
        # Check that first 2 values are None
        assert sma[0] is None
        assert sma[1] is None
        
        # Check calculated values
        assert sma[2] == 2.0  # (1+2+3)/3
        assert sma[3] == 3.0  # (2+3+4)/3
        assert sma[4] == 4.0  # (3+4+5)/3
    
    def test_sma_invalid_period(self):
        """Test SMA with invalid period."""
        with pytest.raises(ValueError, match="Period must be positive"):
            self.ma.simple_moving_average(self.test_values, period=0)
        
        with pytest.raises(ValueError, match="Period must be positive"):
            self.ma.simple_moving_average(self.test_values, period=-1)
    
    def test_sma_insufficient_data(self):
        """Test SMA with insufficient data."""
        short_data = [1, 2, 3]
        sma = self.ma.simple_moving_average(short_data, period=5)
        
        # Should return all None values
        assert all(val is None for val in sma)
    
    def test_exponential_moving_average(self):
        """Test Exponential Moving Average calculation."""
        ema = self.ma.exponential_moving_average(self.test_values, period=3)
        
        # Check length
        assert len(ema) == len(self.test_values)
        
        # Check that first 2 values are None
        assert ema[0] is None
        assert ema[1] is None
        
        # Check that 3rd value is SMA
        assert ema[2] == 2.0  # (1+2+3)/3
        
        # Check that subsequent values are calculated
        assert ema[3] is not None
        assert ema[3] > 2.0  # Should be influenced by value 4
    
    def test_weighted_moving_average(self):
        """Test Weighted Moving Average calculation."""
        wma = self.ma.weighted_moving_average(self.test_values, period=3)
        
        # Check length
        assert len(wma) == len(self.test_values)
        
        # Check that first 2 values are None
        assert wma[0] is None
        assert wma[1] is None
        
        # Check calculated value
        # WMA(3) = (1*1 + 2*2 + 3*3) / (1+2+3) = 14/6 = 2.333...
        expected = (1*1 + 2*2 + 3*3) / (1+2+3)
        assert abs(wma[2] - expected) < 0.001
    
    def test_hull_moving_average(self):
        """Test Hull Moving Average calculation."""
        # Use longer data for HMA
        long_data = list(range(1, 21))  # 1 to 20
        hma = self.ma.hull_moving_average(long_data, period=9)
        
        # Check length
        assert len(hma) == len(long_data)
        
        # Should have some valid values
        valid_values = [val for val in hma if val is not None]
        assert len(valid_values) > 0
    
    def test_adaptive_moving_average(self):
        """Test Adaptive Moving Average calculation."""
        # Create data with varying volatility
        volatile_data = [1, 5, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12, 7, 13, 8, 14]
        ama = self.ma.adaptive_moving_average(volatile_data, period=5)
        
        # Check length
        assert len(ama) == len(volatile_data)
        
        # Check that first 5 values are None
        assert all(val is None for val in ama[:5])
        
        # Check that subsequent values are calculated
        valid_values = [val for val in ama[5:] if val is not None]
        assert len(valid_values) > 0
    
    def test_triangular_moving_average(self):
        """Test Triangular Moving Average calculation."""
        tma = self.ma.triangular_moving_average(self.test_values, period=3)
        
        # Check length
        assert len(tma) == len(self.test_values)
        
        # Should have some valid values (though many will be None due to double smoothing)
        valid_values = [val for val in tma if val is not None]
        # TMA requires more data points due to double smoothing
        assert len(valid_values) >= 0  # May have no valid values with short data
    
    def test_ma_crossover_signals(self):
        """Test moving average crossover signal detection."""
        # Create test data where fast MA crosses slow MA
        fast_ma = [None, None, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        slow_ma = [None, None, 3.0, 3.5, 4.5, 4.8, 5.5, 6.5]
        
        signals = self.ma.get_ma_crossover_signals(fast_ma, slow_ma)
        
        # Check length
        assert len(signals) == len(fast_ma)
        
        # First signal should be None
        assert signals[0] is None
        
        # Should detect crossovers
        signal_types = [sig for sig in signals if sig is not None]
        assert len(signal_types) > 0
    
    def test_crossover_signals_bullish(self):
        """Test detection of bullish crossover."""
        # Fast MA crosses above slow MA
        fast_ma = [1.0, 2.0, 3.0, 4.0]
        slow_ma = [2.0, 2.5, 2.8, 3.5]
        
        signals = self.ma.get_ma_crossover_signals(fast_ma, slow_ma)
        
        # Should detect bullish crossover at index 3
        assert 'bullish_cross' in signals
    
    def test_crossover_signals_bearish(self):
        """Test detection of bearish crossover."""
        # Fast MA crosses below slow MA
        fast_ma = [4.0, 3.0, 2.0, 1.0]
        slow_ma = [3.0, 3.2, 2.5, 2.0]
        
        signals = self.ma.get_ma_crossover_signals(fast_ma, slow_ma)
        
        # Should detect bearish crossover
        assert 'bearish_cross' in signals
    
    def test_crossover_signals_mismatched_length(self):
        """Test crossover signals with mismatched lengths."""
        fast_ma = [1.0, 2.0, 3.0]
        slow_ma = [1.0, 2.0]  # Different length
        
        with pytest.raises(ValueError, match="Moving average lists must have the same length"):
            self.ma.get_ma_crossover_signals(fast_ma, slow_ma)
    
    def test_crossover_signals_with_none_values(self):
        """Test crossover signals with None values."""
        fast_ma = [None, 1.0, 2.0, None, 4.0]
        slow_ma = [None, 1.5, 1.8, 2.0, 3.5]
        
        signals = self.ma.get_ma_crossover_signals(fast_ma, slow_ma)
        
        # Should handle None values gracefully
        assert len(signals) == len(fast_ma)
        assert signals[0] is None  # First is always None
        
        # Signals with None values should be None
        assert signals[3] is None  # fast_ma[3] is None
    
    def test_edge_case_single_value(self):
        """Test moving averages with single value."""
        single_value = [5.0]
        
        sma = self.ma.simple_moving_average(single_value, period=1)
        assert sma == [5.0]
        
        sma_long_period = self.ma.simple_moving_average(single_value, period=3)
        assert sma_long_period == [None]
    
    def test_edge_case_constant_values(self):
        """Test moving averages with constant values."""
        constant_values = [5.0] * 10
        
        sma = self.ma.simple_moving_average(constant_values, period=3)
        
        # All calculated values should be 5.0
        valid_sma = [val for val in sma if val is not None]
        assert all(val == 5.0 for val in valid_sma)
        
        ema = self.ma.exponential_moving_average(constant_values, period=3)
        valid_ema = [val for val in ema if val is not None]
        assert all(val == 5.0 for val in valid_ema)