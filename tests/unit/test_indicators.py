"""Unit tests for technical indicators."""

import pytest
import numpy as np
from cryptvault.indicators.trend import calculate_sma, calculate_ema
from cryptvault.indicators.momentum import calculate_rsi, calculate_macd
from cryptvault.indicators.volatility import calculate_bollinger_bands, calculate_atr


@pytest.mark.unit
@pytest.mark.indicators
class TestTrendIndicators:
    """Test trend indicators."""
    
    def test_sma_calculation(self, sample_price_dataframe):
        """Test SMA calculation."""
        closes = sample_price_dataframe.get_closes()
        sma = calculate_sma(closes, period=10)
        
        assert len(sma) == len(closes)
        # First 9 values should be None
        assert all(v is None for v in sma[:9])
        # 10th value should be average of first 10
        assert sma[9] == pytest.approx(sum(closes[:10]) / 10, rel=0.01)
    
    def test_ema_calculation(self, sample_price_dataframe):
        """Test EMA calculation."""
        closes = sample_price_dataframe.get_closes()
        ema = calculate_ema(closes, period=10)
        
        assert len(ema) == len(closes)
        # First 9 values should be None
        assert all(v is None for v in ema[:9])
        # EMA should be calculated after period
        assert all(v is not None for v in ema[9:])


@pytest.mark.unit
@pytest.mark.indicators
class TestMomentumIndicators:
    """Test momentum indicators."""
    
    def test_rsi_calculation(self, uptrend_price_points):
        """Test RSI calculation."""
        from cryptvault.data.models import PriceDataFrame
        df = PriceDataFrame(uptrend_price_points, symbol='TEST')
        closes = df.get_closes()
        
        rsi = calculate_rsi(closes, period=14)
        
        assert len(rsi) == len(closes)
        # RSI values should be between 0 and 100
        valid_rsi = [v for v in rsi if v is not None]
        assert all(0 <= v <= 100 for v in valid_rsi)
        # Uptrend should have RSI > 50
        assert all(v > 50 for v in valid_rsi)
    
    def test_macd_calculation(self, sample_price_dataframe):
        """Test MACD calculation."""
        closes = sample_price_dataframe.get_closes()
        macd_line, signal_line, histogram = calculate_macd(closes)
        
        assert len(macd_line) == len(closes)
        assert len(signal_line) == len(closes)
        assert len(histogram) == len(closes)


@pytest.mark.unit
@pytest.mark.indicators
class TestVolatilityIndicators:
    """Test volatility indicators."""
    
    def test_bollinger_bands(self, sample_price_dataframe):
        """Test Bollinger Bands calculation."""
        closes = sample_price_dataframe.get_closes()
        upper, middle, lower = calculate_bollinger_bands(closes, period=20, std_dev=2)
        
        assert len(upper) == len(closes)
        assert len(middle) == len(closes)
        assert len(lower) == len(closes)
        
        # Upper should be > middle > lower
        for i in range(19, len(closes)):
            if upper[i] is not None:
                assert upper[i] > middle[i] > lower[i]
    
    def test_atr_calculation(self, sample_price_dataframe):
        """Test ATR calculation."""
        highs = sample_price_dataframe.get_highs()
        lows = sample_price_dataframe.get_lows()
        closes = sample_price_dataframe.get_closes()
        
        atr = calculate_atr(highs, lows, closes, period=14)
        
        assert len(atr) == len(closes)
        # ATR should be positive
        valid_atr = [v for v in atr if v is not None]
        assert all(v > 0 for v in valid_atr)
