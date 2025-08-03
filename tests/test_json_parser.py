"""Tests for JSON parser functionality."""

import pytest
import json
from datetime import datetime
from crypto_chart_analyzer.data.parsers import JSONParser
from crypto_chart_analyzer.data.models import PriceDataFrame


class TestJSONParser:
    """Test cases for JSONParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JSONParser()
        
        # Sample data points
        self.sample_point = {
            "timestamp": "2023-01-01 12:00:00",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0,
            "symbol": "BTC",
            "timeframe": "1h"
        }
        
        self.sample_array = [
            {
                "timestamp": "2023-01-01 12:00:00",
                "open": 100.0,
                "high": 105.0,
                "low": 95.0,
                "close": 102.0,
                "volume": 1000.0
            },
            {
                "timestamp": 1672578000,
                "open": 102.0,
                "high": 108.0,
                "low": 98.0,
                "close": 105.0,
                "volume": 1200.0
            }
        ]
        
        self.structured_json = {
            "symbol": "BTC",
            "timeframe": "1h",
            "data": self.sample_array
        }
    
    def test_parse_single_point_json(self):
        """Test parsing single data point JSON."""
        json_str = json.dumps(self.sample_point)
        result = self.parser.parse(json_str)
        
        assert isinstance(result, PriceDataFrame)
        assert len(result) == 1
        assert result.symbol == "BTC"
        assert result.timeframe == "1h"
        
        point = result[0]
        assert point.open == 100.0
        assert point.high == 105.0
        assert point.low == 95.0
        assert point.close == 102.0
        assert point.volume == 1000.0
        assert point.timestamp == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_parse_array_json(self):
        """Test parsing array of data points JSON."""
        json_str = json.dumps(self.sample_array)
        result = self.parser.parse(json_str)
        
        assert isinstance(result, PriceDataFrame)
        assert len(result) == 2
        assert result.symbol == "UNKNOWN"  # No symbol in array items
        assert result.timeframe == "1h"    # Default
        
        # Check first point
        assert result[0].open == 100.0
        assert result[0].timestamp == datetime(2023, 1, 1, 12, 0, 0)
        
        # Check second point (Unix timestamp)
        assert result[1].open == 102.0
        assert result[1].timestamp == datetime.fromtimestamp(1672578000)
    
    def test_parse_structured_json(self):
        """Test parsing structured JSON with metadata."""
        json_str = json.dumps(self.structured_json)
        result = self.parser.parse(json_str)
        
        assert isinstance(result, PriceDataFrame)
        assert len(result) == 2
        assert result.symbol == "BTC"
        assert result.timeframe == "1h"
        
        # Verify data points
        assert result[0].open == 100.0
        assert result[1].open == 102.0
    
    def test_empty_json_validation(self):
        """Test validation of empty JSON data."""
        with pytest.raises(ValueError, match="JSON data cannot be empty"):
            self.parser.parse("")
        
        with pytest.raises(ValueError, match="JSON data cannot be empty"):
            self.parser.parse("   ")
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON format."""
        invalid_json = '{"timestamp": "2023-01-01", "open": 100.0, invalid}'
        
        with pytest.raises(ValueError, match="Invalid JSON format"):
            self.parser.parse(invalid_json)
    
    def test_missing_required_fields(self):
        """Test validation of missing required fields."""
        incomplete_point = {
            "timestamp": "2023-01-01 12:00:00",
            "open": 100.0,
            "high": 105.0,
            # Missing low, close, volume
        }
        
        json_str = json.dumps(incomplete_point)
        
        with pytest.raises(ValueError, match="Missing required fields"):
            self.parser.parse(json_str)
    
    def test_invalid_price_data(self):
        """Test handling of invalid price data."""
        invalid_point = {
            "timestamp": "2023-01-01 12:00:00",
            "open": "invalid",
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0
        }
        
        json_str = json.dumps(invalid_point)
        
        with pytest.raises(ValueError, match="Invalid data point format"):
            self.parser.parse(json_str)
    
    def test_invalid_timestamp_format(self):
        """Test handling of invalid timestamp."""
        invalid_point = {
            "timestamp": "invalid_timestamp",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0
        }
        
        json_str = json.dumps(invalid_point)
        
        with pytest.raises(ValueError, match="Unable to parse timestamp"):
            self.parser.parse(json_str)
    
    def test_unix_timestamp_parsing(self):
        """Test parsing Unix timestamps."""
        point_with_unix = {
            "timestamp": 1672574400,  # 2023-01-01 12:00:00 UTC
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0
        }
        
        json_str = json.dumps(point_with_unix)
        result = self.parser.parse(json_str)
        
        assert result[0].timestamp == datetime.fromtimestamp(1672574400)
    
    def test_unix_timestamp_milliseconds(self):
        """Test parsing Unix timestamps in milliseconds."""
        point_with_unix_ms = {
            "timestamp": 1672574400000,  # Milliseconds
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0
        }
        
        json_str = json.dumps(point_with_unix_ms)
        result = self.parser.parse(json_str)
        
        assert result[0].timestamp == datetime.fromtimestamp(1672574400)
    
    def test_iso_timestamp_parsing(self):
        """Test parsing ISO format timestamps."""
        point_with_iso = {
            "timestamp": "2023-01-01T12:00:00Z",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0
        }
        
        json_str = json.dumps(point_with_iso)
        result = self.parser.parse(json_str)
        
        assert result[0].timestamp == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_validate_format_valid_single(self):
        """Test format validation with valid single point."""
        assert self.parser.validate_format(self.sample_point) is True
    
    def test_validate_format_valid_array(self):
        """Test format validation with valid array."""
        assert self.parser.validate_format(self.sample_array) is True
    
    def test_validate_format_valid_structured(self):
        """Test format validation with valid structured format."""
        assert self.parser.validate_format(self.structured_json) is True
    
    def test_validate_format_invalid(self):
        """Test format validation with invalid data."""
        invalid_point = {"timestamp": "2023-01-01", "open": 100.0}  # Missing fields
        assert self.parser.validate_format(invalid_point) is False
        
        invalid_array = []  # Empty array
        assert self.parser.validate_format(invalid_array) is False
        
        invalid_structured = {"data": []}  # Empty data array
        assert self.parser.validate_format(invalid_structured) is False
        
        assert self.parser.validate_format("not_dict_or_array") is False
    
    def test_get_sample_format(self):
        """Test sample format documentation."""
        sample = self.parser.get_sample_format()
        
        assert "Array format:" in sample
        assert "Structured format:" in sample
        assert "Single point format:" in sample
        assert "Required fields:" in sample
        assert "Optional fields:" in sample
    
    def test_empty_data_arrays(self):
        """Test handling of empty data arrays."""
        # Empty array
        with pytest.raises(ValueError, match="JSON array cannot be empty"):
            self.parser.parse("[]")
        
        # Structured with empty data
        empty_structured = {"symbol": "BTC", "data": []}
        json_str = json.dumps(empty_structured)
        
        with pytest.raises(ValueError, match="No valid data points found"):
            self.parser.parse(json_str)
    
    def test_array_with_symbol_extraction(self):
        """Test symbol extraction from array items."""
        array_with_symbols = [
            {
                "timestamp": "2023-01-01 12:00:00",
                "open": 100.0,
                "high": 105.0,
                "low": 95.0,
                "close": 102.0,
                "volume": 1000.0,
                "symbol": "BTC",
                "timeframe": "1h"
            },
            {
                "timestamp": "2023-01-01 13:00:00",
                "open": 102.0,
                "high": 108.0,
                "low": 98.0,
                "close": 105.0,
                "volume": 1200.0
            }
        ]
        
        json_str = json.dumps(array_with_symbols)
        result = self.parser.parse(json_str)
        
        # Should extract symbol and timeframe from first item
        assert result.symbol == "BTC"
        assert result.timeframe == "1h"
    
    def test_unsupported_timestamp_type(self):
        """Test handling of unsupported timestamp types."""
        invalid_point = {
            "timestamp": ["not", "a", "timestamp"],  # Array instead of string/number
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000.0
        }
        
        json_str = json.dumps(invalid_point)
        
        with pytest.raises(ValueError, match="Timestamp must be number or string"):
            self.parser.parse(json_str)