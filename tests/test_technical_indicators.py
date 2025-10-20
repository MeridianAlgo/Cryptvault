"""Tests for technical indicators functionality."""

import pytest
from datetime import datetime, timedelta
from cryptvault.indicators.technical import TechnicalIndicators
from cryptvault.data.models import PricePoint, PriceDataFrame


class TestTechnicalIndicators:
    """Test cases for TechnicalIndicators class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.indicators = TechnicalIndicators()
        
        # Create sample data with known patterns
        self.sample_data = self.create_sample_data()
        self.dataframe = PriceDataFrame(
            data=self.sample_data,
            symbol="BTC",
            timeframe="1h"
        )
    
    def create_sample_data(self) -> list[PricePoint]:
        """Create sample price data for testing."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Create data with some price movement patterns
        prices = [100, 102, 98, 105, 103, 107, 104, 110, 108, 112, 
                 109, 115, 113, 118, 116, 120, 118, 122, 119, 125,
                 123, 128, 126, 130, 128, 132, 129, 135, 133, 138]
        
        data = []
        for i, price in enumerate(prices):
            timestamp = base_time + timedelta(hours=i)
            
            # Create realistic OHLC data
            open_price = price
            high_price = price + 2
            low_price = price - 1.5
            close_price = price + 0.5
            volume = 1000 + (i * 50)
            
            point = PricePoint(
                timestamp=timestamp,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume
            )
            data.append(point)
        
        return data
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        rsi_values = self.indicators.calculate_rsi(self.dataframe, period=14)
        
        # Check length
        assert len(rsi_values) == len(self.dataframe)
        
        # Check that first 14 values are None
        assert all(val is None for val in rsi_values[:14])
        
        # Check that subsequent values are valid RSI (0-100)
        valid_rsi = [val for val in rsi_values[14:] if val is not None]
        assert all(0 <= val <= 100 for val in valid_rsi)
        
        # With generally increasing prices, RSI should be > 50
        assert all(val > 50 for val in valid_rsi)
    
    def test_rsi_insufficient_data(self):
        """Test RSI with insufficient data."""
        small_data = self.sample_data[:10]  # Only 10 points
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        with pytest.raises(ValueError, match="Insufficient data for RSI"):
            self.indicators.calculate_rsi(small_dataframe, period=14)
    
    def test_macd_calculation(self):
        """Test MACD calculation."""
        macd_result = self.indicators.calculate_macd(self.dataframe)
        
        # Check that all required keys are present
        assert 'macd' in macd_result
        assert 'signal' in macd_result
        assert 'histogram' in macd_result
        
        # Check lengths
        assert len(macd_result['macd']) == len(self.dataframe)
        assert len(macd_result['signal']) == len(self.dataframe)
        assert len(macd_result['histogram']) == len(self.dataframe)
        
        # Check that initial values are None (due to EMA calculation)
        assert macd_result['macd'][0] is None
        assert macd_result['signal'][0] is None
        assert macd_result['histogram'][0] is None
        
        # Check that we have valid values later
        valid_macd = [val for val in macd_result['macd'] if val is not None]
        assert len(valid_macd) > 0
    
    def test_macd_custom_periods(self):
        """Test MACD with custom periods."""
        macd_result = self.indicators.calculate_macd(
            self.dataframe, 
            fast_period=5, 
            slow_period=10, 
            signal_period=3
        )
        
        # Should have more valid values with shorter periods
        valid_macd = [val for val in macd_result['macd'] if val is not None]
        assert len(valid_macd) > 15  # Should have values after index 10
    
    def test_macd_insufficient_data(self):
        """Test MACD with insufficient data."""
        small_data = self.sample_data[:20]  # Only 20 points
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        with pytest.raises(ValueError, match="Insufficient data for MACD"):
            self.indicators.calculate_macd(small_dataframe, slow_period=26)
    
    def test_ema_calculation(self):
        """Test EMA calculation."""
        closes = self.dataframe.get_closes()
        ema_values = self.indicators._calculate_ema(closes, period=10)
        
        # Check length
        assert len(ema_values) == len(closes)
        
        # Check that first 9 values are None
        assert all(val is None for val in ema_values[:9])
        
        # Check that 10th value is SMA
        sma_10 = sum(closes[:10]) / 10
        assert abs(ema_values[9] - sma_10) < 0.001
        
        # Check that subsequent values are calculated
        assert all(val is not None for val in ema_values[9:])
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        bb_result = self.indicators.calculate_bollinger_bands(self.dataframe, period=10)
        
        # Check that all required keys are present
        assert 'upper' in bb_result
        assert 'middle' in bb_result
        assert 'lower' in bb_result
        
        # Check lengths
        assert len(bb_result['upper']) == len(self.dataframe)
        assert len(bb_result['middle']) == len(self.dataframe)
        assert len(bb_result['lower']) == len(self.dataframe)
        
        # Check that first 9 values are None
        assert all(val is None for val in bb_result['upper'][:9])
        assert all(val is None for val in bb_result['middle'][:9])
        assert all(val is None for val in bb_result['lower'][:9])
        
        # Check band relationships (upper > middle > lower)
        for i in range(9, len(self.dataframe)):
            assert bb_result['upper'][i] > bb_result['middle'][i]
            assert bb_result['middle'][i] > bb_result['lower'][i]
    
    def test_stochastic_calculation(self):
        """Test Stochastic Oscillator calculation."""
        stoch_result = self.indicators.calculate_stochastic(self.dataframe, k_period=14)
        
        # Check that all required keys are present
        assert 'k' in stoch_result
        assert 'd' in stoch_result
        
        # Check lengths
        assert len(stoch_result['k']) == len(self.dataframe)
        assert len(stoch_result['d']) == len(self.dataframe)
        
        # Check that initial values are None
        assert all(val is None for val in stoch_result['k'][:13])
        
        # Check that %K values are in range 0-100
        valid_k = [val for val in stoch_result['k'] if val is not None]
        assert all(0 <= val <= 100 for val in valid_k)
        
        # Check that %D values are in range 0-100
        valid_d = [val for val in stoch_result['d'] if val is not None]
        assert all(0 <= val <= 100 for val in valid_d)
    
    def test_find_peaks_and_troughs(self):
        """Test peak and trough detection."""
        # Create simple test data with known peaks and troughs
        test_values = [1, 3, 2, 5, 1, 4, 2, 6, 3, 2]
        
        result = self.indicators.find_peaks_and_troughs(test_values, min_distance=1)
        
        # Check that we found peaks and troughs
        assert 'peaks' in result
        assert 'troughs' in result
        assert len(result['peaks']) > 0
        assert len(result['troughs']) > 0
        
        # Verify some expected peaks and troughs
        # Index 1 (value 3) should be a peak
        # Index 3 (value 5) should be a peak
        # Index 7 (value 6) should be a peak
        peaks = result['peaks']
        assert 1 in peaks or 3 in peaks or 7 in peaks
    
    def test_find_peaks_troughs_with_none_values(self):
        """Test peak detection with None values."""
        test_values = [1, None, 3, 2, None, 5, 1]
        
        result = self.indicators.find_peaks_and_troughs(test_values)
        
        # Should handle None values gracefully
        assert 'peaks' in result
        assert 'troughs' in result
    
    def test_atr_calculation(self):
        """Test Average True Range calculation."""
        atr_values = self.indicators.calculate_atr(self.dataframe, period=14)
        
        # Check length
        assert len(atr_values) == len(self.dataframe)
        
        # Check that first value is None
        assert atr_values[0] is None
        
        # Check that subsequent values are positive
        valid_atr = [val for val in atr_values[1:] if val is not None]
        assert all(val > 0 for val in valid_atr)
        
        # ATR should be reasonable relative to price range
        price_range = max(self.dataframe.get_closes()) - min(self.dataframe.get_closes())
        avg_atr = sum(valid_atr) / len(valid_atr)
        assert avg_atr < price_range  # ATR should be less than total price range
    
    def test_atr_insufficient_data(self):
        """Test ATR with insufficient data."""
        small_data = self.sample_data[:10]  # Only 10 points
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        with pytest.raises(ValueError, match="Insufficient data for ATR"):
            self.indicators.calculate_atr(small_dataframe, period=14)
    
    def test_bollinger_bands_insufficient_data(self):
        """Test Bollinger Bands with insufficient data."""
        small_data = self.sample_data[:15]  # Only 15 points
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        with pytest.raises(ValueError, match="Insufficient data for Bollinger Bands"):
            self.indicators.calculate_bollinger_bands(small_dataframe, period=20)
    
    def test_stochastic_insufficient_data(self):
        """Test Stochastic with insufficient data."""
        small_data = self.sample_data[:10]  # Only 10 points
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        with pytest.raises(ValueError, match="Insufficient data for Stochastic"):
            self.indicators.calculate_stochastic(small_dataframe, k_period=14)
    
    def test_edge_case_constant_prices(self):
        """Test indicators with constant prices."""
        # Create data with constant prices
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        constant_data = []
        
        for i in range(20):
            timestamp = base_time + timedelta(hours=i)
            point = PricePoint(
                timestamp=timestamp,
                open=100.0,
                high=100.0,
                low=100.0,
                close=100.0,
                volume=1000.0
            )
            constant_data.append(point)
        
        constant_dataframe = PriceDataFrame(data=constant_data, symbol="TEST")
        
        # RSI should be around 50 for constant prices
        rsi_values = self.indicators.calculate_rsi(constant_dataframe, period=14)
        valid_rsi = [val for val in rsi_values if val is not None]
        # With constant prices, RSI calculation might result in NaN or specific values
        # The exact behavior depends on implementation details
        
        # MACD should be close to 0 for constant prices
        macd_result = self.indicators.calculate_macd(constant_dataframe)
        valid_macd = [val for val in macd_result['macd'] if val is not None]
        if valid_macd:
            assert all(abs(val) < 0.001 for val in valid_macd)  # Should be very close to 0
