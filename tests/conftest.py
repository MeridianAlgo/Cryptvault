"""
Pytest Configuration and Shared Fixtures

This module provides shared fixtures and configuration for all tests.
Fixtures include sample data, mock objects, and common test utilities.
"""

import pytest
from datetime import datetime, timedelta
from typing import List
import numpy as np

from cryptvault.data.models import PricePoint, PriceDataFrame


@pytest.fixture
def sample_price_points() -> List[PricePoint]:
    """
    Create sample price points for testing.
    
    Returns 30 days of sample price data with realistic OHLCV values.
    """
    base_price = 50000.0
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    points = []
    
    for i in range(30):
        # Simulate price movement with some volatility
        trend = i * 100  # Upward trend
        volatility = np.random.uniform(-500, 500)
        
        close = base_price + trend + volatility
        open_price = close + np.random.uniform(-200, 200)
        high = max(open_price, close) + abs(np.random.uniform(0, 300))
        low = min(open_price, close) - abs(np.random.uniform(0, 300))
        volume = np.random.uniform(1000000, 5000000)
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        points.append(point)
    
    return points


@pytest.fixture
def sample_price_dataframe(sample_price_points) -> PriceDataFrame:
    """
    Create sample PriceDataFrame for testing.
    
    Uses sample_price_points fixture to create a complete dataframe.
    """
    return PriceDataFrame(
        data=sample_price_points,
        symbol='BTC',
        timeframe='1d'
    )


@pytest.fixture
def sample_ticker_info() -> dict:
    """Create sample ticker information for testing."""
    return {
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'type': 'crypto',
        'exchange': 'Binance',
        'currency': 'USD',
        'market_cap': 1000000000000.0,
        'description': 'Bitcoin is a decentralized digital currency'
    }


@pytest.fixture
def uptrend_price_points() -> List[PricePoint]:
    """Create price points showing clear uptrend."""
    base_price = 40000.0
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    points = []
    
    for i in range(30):
        close = base_price + (i * 500)  # Strong uptrend
        open_price = close - 100
        high = close + 200
        low = open_price - 100
        volume = 2000000.0
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        points.append(point)
    
    return points


@pytest.fixture
def downtrend_price_points() -> List[PricePoint]:
    """Create price points showing clear downtrend."""
    base_price = 60000.0
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    points = []
    
    for i in range(30):
        close = base_price - (i * 500)  # Strong downtrend
        open_price = close + 100
        high = open_price + 100
        low = close - 200
        volume = 2000000.0
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        points.append(point)
    
    return points


@pytest.fixture
def sideways_price_points() -> List[PricePoint]:
    """Create price points showing sideways/ranging market."""
    base_price = 50000.0
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    points = []
    
    for i in range(30):
        # Oscillate around base price
        close = base_price + np.sin(i * 0.5) * 500
        open_price = close + np.random.uniform(-100, 100)
        high = max(open_price, close) + abs(np.random.uniform(0, 200))
        low = min(open_price, close) - abs(np.random.uniform(0, 200))
        volume = 2000000.0
        
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        points.append(point)
    
    return points


@pytest.fixture
def minimal_price_points() -> List[PricePoint]:
    """Create minimal valid price data (just enough for basic tests)."""
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    points = []
    
    for i in range(5):
        point = PricePoint(
            timestamp=base_time + timedelta(days=i),
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=1000000.0
        )
        points.append(point)
    
    return points


@pytest.fixture
def empty_price_points() -> List[PricePoint]:
    """Create empty price points list for testing error handling."""
    return []


@pytest.fixture
def mock_api_response_success():
    """Mock successful API response data."""
    return {
        'success': True,
        'data': {
            'symbol': 'BTC',
            'prices': [
                {'timestamp': '2024-01-01T00:00:00', 'open': 50000, 'high': 51000, 
                 'low': 49000, 'close': 50500, 'volume': 1000000}
            ]
        }
    }


@pytest.fixture
def mock_api_response_error():
    """Mock failed API response data."""
    return {
        'success': False,
        'error': 'API rate limit exceeded',
        'code': 429
    }


@pytest.fixture
def sample_csv_data() -> str:
    """Create sample CSV data for parser testing."""
    return """timestamp,open,high,low,close,volume
2024-01-01 00:00:00,50000.0,51000.0,49000.0,50500.0,1000000.0
2024-01-02 00:00:00,50500.0,51500.0,50000.0,51000.0,1200000.0
2024-01-03 00:00:00,51000.0,52000.0,50500.0,51500.0,1100000.0
"""


@pytest.fixture
def sample_json_data() -> str:
    """Create sample JSON data for parser testing."""
    return """{
    "symbol": "BTC",
    "interval": "1d",
    "data": [
        {
            "timestamp": "2024-01-01T00:00:00",
            "open": 50000.0,
            "high": 51000.0,
            "low": 49000.0,
            "close": 50500.0,
            "volume": 1000000.0
        },
        {
            "timestamp": "2024-01-02T00:00:00",
            "open": 50500.0,
            "high": 51500.0,
            "low": 50000.0,
            "close": 51000.0,
            "volume": 1200000.0
        }
    ]
}"""


# Test configuration fixtures
@pytest.fixture
def test_config():
    """Provide test configuration settings."""
    return {
        'min_data_points': 5,
        'max_data_points': 1000,
        'default_sensitivity': 0.5,
        'enable_ml': False,
        'enable_charts': False
    }


# Marker helpers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
