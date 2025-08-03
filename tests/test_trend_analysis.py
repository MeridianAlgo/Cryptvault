"""Tests for trend analysis functionality."""

import pytest
from datetime import datetime, timedelta
from crypto_chart_analyzer.indicators.trend_analysis import TrendAnalysis, TrendLine, PeakTrough
from crypto_chart_analyzer.data.models import PricePoint, PriceDataFrame


class TestTrendAnalysis:
    """Test cases for TrendAnalysis class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.trend_analysis = TrendAnalysis()
        
        # Create sample data with clear trend
        self.uptrend_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.downtrend_values = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        self.sideways_values = [5, 5.1, 4.9, 5.2, 4.8, 5.0, 5.1, 4.9, 5.0, 5.1]
        
        # Create sample price data
        self.sample_dataframe = self.create_sample_dataframe()
    
    def create_sample_dataframe(self) -> PriceDataFrame:
        """Create sample price dataframe for testing."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Create data with peaks and troughs
        prices = [100, 105, 102, 110, 108, 115, 112, 120, 118, 125, 
                 122, 130, 128, 135, 132, 140, 138, 145, 142, 150]
        
        data = []
        for i, price in enumerate(prices):
            timestamp = base_time + timedelta(hours=i)
            
            point = PricePoint(
                timestamp=timestamp,
                open=price,
                high=price + 2,
                low=price - 2,
                close=price + 1,
                volume=1000 + (i * 50)
            )
            data.append(point)
        
        return PriceDataFrame(data=data, symbol="BTC", timeframe="1h")
    
    def test_fit_trend_line_uptrend(self):
        """Test trend line fitting for uptrend."""
        trend_line = self.trend_analysis.fit_trend_line(self.uptrend_values)
        
        assert isinstance(trend_line, TrendLine)
        assert trend_line.slope > 0  # Positive slope for uptrend
        assert trend_line.r_squared > 0.9  # High correlation for linear data
        assert trend_line.start_index == 0
        assert trend_line.end_index == len(self.uptrend_values) - 1
    
    def test_fit_trend_line_downtrend(self):
        """Test trend line fitting for downtrend."""
        trend_line = self.trend_analysis.fit_trend_line(self.downtrend_values)
        
        assert trend_line.slope < 0  # Negative slope for downtrend
        assert trend_line.r_squared > 0.9  # High correlation
    
    def test_fit_trend_line_custom_range(self):
        """Test trend line fitting with custom range."""
        trend_line = self.trend_analysis.fit_trend_line(
            self.uptrend_values, 
            start_index=2, 
            end_index=7
        )
        
        assert trend_line.start_index == 2
        assert trend_line.end_index == 7
        assert trend_line.slope > 0
    
    def test_fit_trend_line_invalid_range(self):
        """Test trend line fitting with invalid range."""
        with pytest.raises(ValueError, match="Invalid start/end indices"):
            self.trend_analysis.fit_trend_line(self.uptrend_values, start_index=5, end_index=3)
        
        with pytest.raises(ValueError, match="Invalid start/end indices"):
            self.trend_analysis.fit_trend_line(self.uptrend_values, start_index=-1, end_index=5)
    
    def test_fit_trend_line_insufficient_data(self):
        """Test trend line fitting with insufficient data."""
        with pytest.raises(ValueError, match="Need at least 2 valid data points"):
            self.trend_analysis.fit_trend_line([None, None, None])
    
    def test_trend_line_methods(self):
        """Test TrendLine class methods."""
        trend_line = self.trend_analysis.fit_trend_line(self.uptrend_values)
        
        # Test get_value_at_index
        value_at_5 = trend_line.get_value_at_index(5)
        expected = trend_line.slope * 5 + trend_line.intercept
        assert abs(value_at_5 - expected) < 0.001
        
        # Test get_angle_degrees
        angle = trend_line.get_angle_degrees()
        assert isinstance(angle, float)
        assert angle > 0  # Positive angle for uptrend
    
    def test_find_peaks_and_troughs(self):
        """Test peak and trough detection."""
        # Create data with clear peaks and troughs
        test_values = [1, 3, 2, 5, 1, 4, 2, 6, 3, 2, 7, 4]
        
        peaks_troughs = self.trend_analysis.find_peaks_and_troughs(test_values, min_distance=1)
        
        # Should find both peaks and troughs
        peaks = [pt for pt in peaks_troughs if pt.type == 'peak']
        troughs = [pt for pt in peaks_troughs if pt.type == 'trough']
        
        assert len(peaks) > 0
        assert len(troughs) > 0
        
        # Check that all peaks and troughs have valid properties
        for pt in peaks_troughs:
            assert isinstance(pt, PeakTrough)
            assert pt.type in ['peak', 'trough']
            assert 0 <= pt.strength <= 1
            assert pt.index >= 0
    
    def test_find_peaks_troughs_with_prominence(self):
        """Test peak detection with prominence threshold."""
        # Create data with small and large peaks
        test_values = [5, 5.1, 5, 10, 5, 5.05, 5, 15, 5]
        
        # With high prominence threshold, should only find significant peaks
        peaks_troughs = self.trend_analysis.find_peaks_and_troughs(
            test_values, 
            prominence_threshold=0.1  # 10% of range
        )
        
        peaks = [pt for pt in peaks_troughs if pt.type == 'peak']
        
        # Should find the significant peaks (10 and 15) but not the small one (5.1)
        assert len(peaks) >= 1
        assert all(pt.value >= 10 for pt in peaks)
    
    def test_find_peaks_troughs_min_distance(self):
        """Test peak detection with minimum distance."""
        test_values = [1, 3, 2, 4, 3, 5, 4, 6, 5]
        
        # With large min_distance, should find fewer peaks
        peaks_troughs_large_dist = self.trend_analysis.find_peaks_and_troughs(
            test_values, 
            min_distance=5
        )
        
        peaks_troughs_small_dist = self.trend_analysis.find_peaks_and_troughs(
            test_values, 
            min_distance=1
        )
        
        # Should find fewer peaks with larger minimum distance
        assert len(peaks_troughs_large_dist) <= len(peaks_troughs_small_dist)
    
    def test_find_support_resistance_levels(self):
        """Test support and resistance level identification."""
        levels = self.trend_analysis.find_support_resistance_levels(self.sample_dataframe)
        
        assert 'support' in levels
        assert 'resistance' in levels
        assert isinstance(levels['support'], list)
        assert isinstance(levels['resistance'], list)
        
        # Should find some levels
        assert len(levels['support']) > 0 or len(levels['resistance']) > 0
    
    def test_detect_trend_direction_uptrend(self):
        """Test trend direction detection for uptrend."""
        trend = self.trend_analysis.detect_trend_direction(self.uptrend_values)
        assert trend == 'uptrend'
    
    def test_detect_trend_direction_downtrend(self):
        """Test trend direction detection for downtrend."""
        trend = self.trend_analysis.detect_trend_direction(self.downtrend_values)
        assert trend == 'downtrend'
    
    def test_detect_trend_direction_sideways(self):
        """Test trend direction detection for sideways trend."""
        trend = self.trend_analysis.detect_trend_direction(self.sideways_values)
        assert trend == 'sideways'
    
    def test_detect_trend_direction_insufficient_data(self):
        """Test trend direction with insufficient data."""
        short_data = [1, 2, 3]
        trend = self.trend_analysis.detect_trend_direction(short_data, period=10)
        assert trend == 'sideways'
    
    def test_find_trend_channels(self):
        """Test trend channel detection."""
        channels = self.trend_analysis.find_trend_channels(self.sample_dataframe, min_touches=2)
        
        assert isinstance(channels, list)
        
        # Check channel structure if any found
        for channel in channels:
            assert 'upper_line' in channel
            assert 'lower_line' in channel
            assert 'touches' in channel
            assert 'width' in channel
            
            assert channel['touches'] >= 2  # Should meet minimum touches requirement
            
            # Check line structure
            for line_key in ['upper_line', 'lower_line']:
                line = channel[line_key]
                assert 'start' in line
                assert 'end' in line
                assert 'slope' in line
    
    def test_cluster_levels(self):
        """Test level clustering functionality."""
        # Create levels that should be clustered
        levels = [100.0, 100.5, 101.0, 150.0, 150.2, 151.0, 200.0]
        
        clustered = self.trend_analysis._cluster_levels(levels, tolerance=0.02)
        
        # Should have fewer clustered levels than original
        assert len(clustered) <= len(levels)
        assert len(clustered) == 3  # Should cluster into 3 groups around 100, 150, 200
    
    def test_cluster_levels_empty(self):
        """Test level clustering with empty input."""
        clustered = self.trend_analysis._cluster_levels([])
        assert clustered == []
    
    def test_calculate_prominence(self):
        """Test prominence calculation."""
        test_values = [1, 2, 5, 2, 1]  # Clear peak at index 2
        
        prominence = self.trend_analysis._calculate_prominence(test_values, 2, 'peak')
        
        # Prominence should be positive for a clear peak
        assert prominence > 0
        
        # Test trough prominence
        trough_values = [5, 4, 1, 4, 5]  # Clear trough at index 2
        trough_prominence = self.trend_analysis._calculate_prominence(trough_values, 2, 'trough')
        
        assert trough_prominence > 0
    
    def test_count_channel_touches(self):
        """Test channel touch counting."""
        # Create simple test data
        highs = [5, 6, 7, 8, 9]
        lows = [1, 2, 3, 4, 5]
        
        # Create mock peak and trough objects
        peak1 = PeakTrough(0, 5, 'peak', 1.0)
        peak2 = PeakTrough(4, 9, 'peak', 1.0)
        trough1 = PeakTrough(0, 1, 'trough', 1.0)
        trough2 = PeakTrough(4, 5, 'trough', 1.0)
        
        touches = self.trend_analysis._count_channel_touches(
            highs, lows, peak1, peak2, trough1, trough2
        )
        
        # Should count at least the 4 defining points
        assert touches >= 4
    
    def test_edge_cases_with_none_values(self):
        """Test handling of None values in various methods."""
        values_with_none = [1, None, 3, None, 5, 6, None, 8, 9, 10]
        
        # Should handle None values gracefully
        peaks_troughs = self.trend_analysis.find_peaks_and_troughs(values_with_none)
        assert isinstance(peaks_troughs, list)
        
        # Trend line fitting should work with None values
        try:
            trend_line = self.trend_analysis.fit_trend_line(values_with_none)
            assert isinstance(trend_line, TrendLine)
        except ValueError:
            # May raise ValueError if too many None values, which is acceptable
            pass
    
    def test_trend_direction_with_none_values(self):
        """Test trend direction detection with None values."""
        values_with_none = [1, None, 3, None, 5, 6, None, 8, 9, 10]
        
        trend = self.trend_analysis.detect_trend_direction(values_with_none)
        assert trend in ['uptrend', 'downtrend', 'sideways']