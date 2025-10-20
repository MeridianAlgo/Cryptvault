"""Tests for core data models."""

import pytest
from datetime import datetime, timedelta
from cryptvault.data.models import PricePoint, PriceDataFrame


class TestPricePoint:
    """Test cases for PricePoint class."""
    
    def test_valid_price_point(self):
        """Test creating a valid price point."""
        timestamp = datetime.now()
        point = PricePoint(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0
        )
        
        assert point.timestamp == timestamp
        assert point.open == 100.0
        assert point.high == 105.0
        assert point.low == 95.0
        assert point.close == 102.0
        assert point.volume == 1000.0
    
    def test_invalid_high_price(self):
        """Test validation of high price."""
        with pytest.raises(ValueError, match="High price must be"):
            PricePoint(
                timestamp=datetime.now(),
                open=100.0,
                high=95.0,  # Invalid: high < open
                low=90.0,
                close=98.0,
                volume=1000.0
            )
    
    def test_invalid_low_price(self):
        """Test validation of low price."""
        with pytest.raises(ValueError, match="Low price must be"):
            PricePoint(
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=102.0,  # Invalid: low > close
                close=98.0,
                volume=1000.0
            )
    
    def test_negative_volume(self):
        """Test validation of negative volume."""
        with pytest.raises(ValueError, match="Volume cannot be negative"):
            PricePoint(
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=95.0,
                close=102.0,
                volume=-100.0  # Invalid: negative volume
            )


class TestPriceDataFrame:
    """Test cases for PriceDataFrame class."""
    
    def create_sample_data(self, num_points: int = 5) -> list[PricePoint]:
        """Create sample price data for testing."""
        base_time = datetime.now()
        data = []
        
        for i in range(num_points):
            timestamp = base_time + timedelta(hours=i)
            price = 100.0 + i * 2  # Gradually increasing price
            
            point = PricePoint(
                timestamp=timestamp,
                open=price,
                high=price + 2,
                low=price - 1,
                close=price + 1,
                volume=1000.0 + i * 100
            )
            data.append(point)
        
        return data
    
    def test_valid_dataframe(self):
        """Test creating a valid PriceDataFrame."""
        data = self.create_sample_data()
        df = PriceDataFrame(data=data, symbol="BTC", timeframe="1h")
        
        assert len(df) == 5
        assert df.symbol == "BTC"
        assert df.timeframe == "1h"
    
    def test_empty_data_validation(self):
        """Test validation of empty data."""
        with pytest.raises(ValueError, match="Price data cannot be empty"):
            PriceDataFrame(data=[], symbol="BTC")
    
    def test_data_sorting(self):
        """Test that data is sorted by timestamp."""
        data = self.create_sample_data()
        # Shuffle the data
        data = [data[2], data[0], data[4], data[1], data[3]]
        
        df = PriceDataFrame(data=data, symbol="BTC")
        
        # Verify data is sorted
        timestamps = df.get_timestamps()
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1]
    
    def test_get_methods(self):
        """Test getter methods for price data."""
        data = self.create_sample_data()
        df = PriceDataFrame(data=data, symbol="BTC")
        
        opens = df.get_opens()
        highs = df.get_highs()
        lows = df.get_lows()
        closes = df.get_closes()
        volumes = df.get_volumes()
        
        assert len(opens) == 5
        assert len(highs) == 5
        assert len(lows) == 5
        assert len(closes) == 5
        assert len(volumes) == 5
        
        # Verify first point
        assert opens[0] == 100.0
        assert highs[0] == 102.0
        assert lows[0] == 99.0
        assert closes[0] == 101.0
        assert volumes[0] == 1000.0
    
    def test_slice_method(self):
        """Test slicing functionality."""
        data = self.create_sample_data()
        df = PriceDataFrame(data=data, symbol="BTC")
        
        sliced = df.slice(1, 4)
        
        assert len(sliced) == 3
        assert sliced.symbol == "BTC"
        assert sliced[0].open == 102.0  # Second point
    
    def test_invalid_slice(self):
        """Test invalid slice parameters."""
        data = self.create_sample_data()
        df = PriceDataFrame(data=data, symbol="BTC")
        
        with pytest.raises(ValueError, match="Invalid slice indices"):
            df.slice(-1, 3)
        
        with pytest.raises(ValueError, match="Invalid slice indices"):
            df.slice(3, 10)
        
        with pytest.raises(ValueError, match="Invalid slice indices"):
            df.slice(3, 2)
    
    def test_statistics(self):
        """Test statistics calculation."""
        data = self.create_sample_data()
        df = PriceDataFrame(data=data, symbol="BTC")
        
        stats = df.get_statistics()
        
        assert stats["symbol"] == "BTC"
        assert stats["timeframe"] == "1h"
        assert stats["data_points"] == 5
        assert "date_range" in stats
        assert "price_range" in stats
        assert "avg_close" in stats
        assert "avg_volume" in stats
        assert "total_volume" in stats
