"""Unit tests for data models."""

import pytest
from datetime import datetime, timedelta
from cryptvault.data.models import PricePoint, PriceDataFrame


@pytest.mark.unit
@pytest.mark.data
class TestPricePoint:
    """Test PricePoint data model."""
    
    def test_valid_price_point_creation(self, sample_price_points):
        """Test creating valid price point."""
        point = sample_price_points[0]
        assert isinstance(point, PricePoint)
        assert point.open > 0
        assert point.high >= point.open
        assert point.low <= point.close
        assert point.volume >= 0
    
    def test_price_point_basic_attributes(self):
        """Test price point basic attributes."""
        point = PricePoint(
            timestamp=datetime(2024, 1, 1),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            volume=1000000.0
        )
        
        assert point.open == 100.0
        assert point.high == 110.0
        assert point.low == 95.0
        assert point.close == 105.0
        assert point.volume == 1000000.0
        assert isinstance(point.timestamp, datetime)


@pytest.mark.unit
@pytest.mark.data
class TestPriceDataFrame:
    """Test PriceDataFrame data model."""
    
    def test_valid_dataframe_creation(self, sample_price_dataframe):
        """Test creating valid dataframe."""
        assert len(sample_price_dataframe) == 30
        assert sample_price_dataframe.symbol == 'BTC'
        assert sample_price_dataframe.timeframe == '1d'
    
    def test_dataframe_getters(self, sample_price_dataframe):
        """Test dataframe getter methods."""
        closes = sample_price_dataframe.get_closes()
        highs = sample_price_dataframe.get_highs()
        lows = sample_price_dataframe.get_lows()
        volumes = sample_price_dataframe.get_volumes()
        timestamps = sample_price_dataframe.get_timestamps()
        
        assert len(closes) == 30
        assert len(highs) == 30
        assert len(lows) == 30
        assert len(volumes) == 30
        assert len(timestamps) == 30
        
        # Verify high >= low for all points
        for h, l in zip(highs, lows):
            assert h >= l
    
    def test_dataframe_indexing(self, sample_price_dataframe):
        """Test dataframe indexing."""
        first_point = sample_price_dataframe[0]
        assert isinstance(first_point, PricePoint)
        assert first_point.open > 0
        
        last_point = sample_price_dataframe[-1]
        assert isinstance(last_point, PricePoint)
    
    def test_empty_dataframe_creation(self, empty_price_points):
        """Test creating dataframe with empty data."""
        # The current implementation doesn't validate empty data
        df = PriceDataFrame(empty_price_points, symbol='BTC')
        assert len(df) == 0


@pytest.mark.unit
@pytest.mark.data
class TestTickerInfo:
    """Test TickerInfo data model."""
    
    def test_valid_ticker_info(self, sample_ticker_info):
        """Test creating valid ticker info."""
        assert sample_ticker_info['symbol'] == 'BTC'
        assert sample_ticker_info['name'] == 'Bitcoin'
        assert sample_ticker_info['type'] == 'crypto'
        assert sample_ticker_info['exchange'] == 'Binance'
