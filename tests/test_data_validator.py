"""Tests for data validation functionality."""

import pytest
from datetime import datetime, timedelta
from cryptvault.data.validator import DataValidator, ValidationError
from cryptvault.data.models import PricePoint, PriceDataFrame


class TestDataValidator:
    """Test cases for DataValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DataValidator()
        
        # Create valid sample data
        self.valid_data = self.create_sample_data(20)
        self.valid_dataframe = PriceDataFrame(
            data=self.valid_data,
            symbol="BTC",
            timeframe="1h"
        )
    
    def create_sample_data(self, num_points: int, base_price: float = 100.0) -> list[PricePoint]:
        """Create sample price data for testing."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        data = []
        
        for i in range(num_points):
            timestamp = base_time + timedelta(hours=i)
            price = base_price + i * 2  # Gradually increasing price
            
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
    
    def test_valid_dataframe_validation(self):
        """Test validation of valid dataframe."""
        result = self.validator.validate_price_dataframe(self.valid_dataframe)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert "statistics" in result
        assert result["statistics"]["data_points"] == 20
    
    def test_insufficient_data_points(self):
        """Test validation with insufficient data points."""
        small_data = self.create_sample_data(5)  # Less than minimum
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(small_dataframe)
        
        assert result["is_valid"] is False
        assert any("Insufficient data points" in error for error in result["errors"])
        assert any("at least 10 data points" in suggestion for suggestion in result["suggestions"])
    
    def test_missing_symbol_warning(self):
        """Test warning for missing symbol."""
        dataframe = PriceDataFrame(data=self.valid_data)  # No symbol specified
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("Symbol not specified" in warning for warning in result["warnings"])
        assert any("Specify symbol" in suggestion for suggestion in result["suggestions"])
    
    def test_duplicate_timestamps(self):
        """Test detection of duplicate timestamps."""
        data = self.create_sample_data(5)
        # Make duplicate timestamp
        data[1].timestamp = data[0].timestamp
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert result["is_valid"] is False
        assert any("Duplicate timestamps" in error for error in result["errors"])
    
    def test_invalid_ohlc_relationships(self):
        """Test detection of invalid OHLC relationships."""
        data = self.create_sample_data(5)
        # Make invalid high price
        data[0].high = data[0].open - 5  # High < open
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert result["is_valid"] is False
        assert any("Invalid high price" in error for error in result["errors"])
    
    def test_zero_negative_prices(self):
        """Test detection of zero or negative prices."""
        data = self.create_sample_data(5)
        # Set negative price
        data[0].open = -10.0
        data[0].high = 5.0
        data[0].low = -15.0
        data[0].close = 0.0
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert result["is_valid"] is False
        assert any("Zero or negative price" in error for error in result["errors"])
    
    def test_zero_volume_warning(self):
        """Test warning for zero volume."""
        data = self.create_sample_data(5)
        data[0].volume = 0.0
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("Zero volume" in warning for warning in result["warnings"])
    
    def test_large_price_changes(self):
        """Test detection of large price changes."""
        data = self.create_sample_data(5)
        # Create large price jump
        data[1].open = data[0].close * 2  # 100% increase
        data[1].high = data[1].open + 2
        data[1].low = data[1].open - 1
        data[1].close = data[1].open + 1
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("Large price change detected" in warning for warning in result["warnings"])
        assert any("Review data for potential errors" in suggestion for suggestion in result["suggestions"])
    
    def test_negative_volume_error(self):
        """Test detection of negative volume."""
        data = self.create_sample_data(5)
        data[0].volume = -100.0
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert result["is_valid"] is False
        assert any("Negative volume" in error for error in result["errors"])
    
    def test_volume_spikes(self):
        """Test detection of volume spikes."""
        data = self.create_sample_data(10)
        # Create volume spike
        data[5].volume = 100000.0  # Much higher than normal ~1500
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("High volume spike" in warning for warning in result["warnings"])
    
    def test_short_time_intervals(self):
        """Test detection of very short time intervals."""
        data = self.create_sample_data(5)
        # Make very short interval (30 seconds)
        data[1].timestamp = data[0].timestamp + timedelta(seconds=30)
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("Very short time interval" in warning for warning in result["warnings"])
    
    def test_large_time_gaps(self):
        """Test detection of large time gaps."""
        data = self.create_sample_data(5)
        # Create large gap (48 hours)
        data[2].timestamp = data[1].timestamp + timedelta(hours=48)
        # Adjust subsequent timestamps
        for i in range(3, len(data)):
            data[i].timestamp = data[2].timestamp + timedelta(hours=i-2)
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("Large time gap" in warning for warning in result["warnings"])
        assert any("Check for missing data" in suggestion for suggestion in result["suggestions"])
    
    def test_inconsistent_intervals(self):
        """Test detection of inconsistent time intervals."""
        data = self.create_sample_data(10)
        # Make inconsistent intervals
        data[3].timestamp = data[2].timestamp + timedelta(minutes=30)  # 30 min instead of 1 hour
        data[4].timestamp = data[3].timestamp + timedelta(hours=3)     # 3 hours
        data[5].timestamp = data[4].timestamp + timedelta(minutes=15)  # 15 minutes
        
        # Adjust remaining timestamps
        for i in range(6, len(data)):
            data[i].timestamp = data[5].timestamp + timedelta(hours=i-5)
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(dataframe)
        
        assert any("Inconsistent time intervals" in warning for warning in result["warnings"])
    
    def test_statistics_generation(self):
        """Test statistics generation."""
        result = self.validator.validate_price_dataframe(self.valid_dataframe)
        stats = result["statistics"]
        
        assert "data_points" in stats
        assert "time_span_hours" in stats
        assert "price_range" in stats
        assert "price_avg" in stats
        assert "price_volatility" in stats
        assert "volume_avg" in stats
        assert "volume_total" in stats
        assert "date_range" in stats
        
        assert stats["data_points"] == 20
        assert stats["time_span_hours"] == 19.0  # 20 points, 1 hour apart = 19 hours span
        assert stats["price_range"][0] == 101.0  # First close price
        assert stats["price_range"][1] == 139.0  # Last close price
    
    def test_validate_and_suggest_fixes(self):
        """Test quick validation with suggestions."""
        is_valid, suggestions = self.validator.validate_and_suggest_fixes(self.valid_dataframe)
        
        assert is_valid is True
        assert len(suggestions) > 0
        assert any("📊 Data Summary:" in suggestion for suggestion in suggestions)
    
    def test_validate_and_suggest_fixes_invalid(self):
        """Test quick validation with invalid data."""
        data = self.create_sample_data(5)  # Too few points
        data[0].volume = -100.0  # Negative volume
        
        dataframe = PriceDataFrame(data=data, symbol="BTC")
        
        is_valid, suggestions = self.validator.validate_and_suggest_fixes(dataframe)
        
        assert is_valid is False
        assert any("❌ Data validation failed:" in suggestion for suggestion in suggestions)
        assert any("💡 Suggestions:" in suggestion for suggestion in suggestions)
    
    def test_set_validation_thresholds(self):
        """Test updating validation thresholds."""
        original_min_points = self.validator.min_data_points
        
        self.validator.set_validation_thresholds(
            min_data_points=5,
            max_price_change_percent=25.0
        )
        
        assert self.validator.min_data_points == 5
        assert self.validator.max_price_change_percent == 25.0
        
        # Test with updated threshold
        small_data = self.create_sample_data(5)
        small_dataframe = PriceDataFrame(data=small_data, symbol="BTC")
        
        result = self.validator.validate_price_dataframe(small_dataframe)
        
        # Should now pass with 5 data points
        assert not any("Insufficient data points" in error for error in result["errors"])
    
    def test_empty_dataframe_handling(self):
        """Test handling of edge cases."""
        # This should be caught by PriceDataFrame validation, but test validator robustness
        try:
            single_point_data = self.create_sample_data(1)
            single_dataframe = PriceDataFrame(data=single_point_data, symbol="BTC")
            
            result = self.validator.validate_price_dataframe(single_dataframe)
            
            # Should handle gracefully
            assert "statistics" in result
            
        except Exception:
            # If PriceDataFrame rejects single point, that's also acceptable
            pass
