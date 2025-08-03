"""Tests for CSV parser functionality."""

import pytest
from datetime import datetime
from crypto_chart_analyzer.data.parsers import CSVParser
from crypto_chart_analyzer.data.models import PriceDataFrame


class TestCSVParser:
    """Test cases for CSVParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CSVParser()
        
        # Sample valid CSV data
        self.valid_csv = """timestamp,open,high,low,close,volume,symbol,timeframe
2023-01-01 12:00:00,100.0,105.0,95.0,102.0,1000.0,BTC,1h
2023-01-01 13:00:00,102.0,108.0,98.0,105.0,1200.0,BTC,1h
2023-01-01 14:00:00,105.0,110.0,100.0,107.0,1100.0,BTC,1h"""
        
        # Minimal CSV without optional columns
        self.minimal_csv = """timestamp,open,high,low,close,volume
2023-01-01 12:00:00,100.0,105.0,95.0,102.0,1000.0
2023-01-01 13:00:00,102.0,108.0,98.0,105.0,1200.0"""
    
    def test_valid_csv_parsing(self):
        """Test parsing valid CSV data."""
        result = self.parser.parse(self.valid_csv)
        
        assert isinstance(result, PriceDataFrame)
        assert len(result) == 3
        assert result.symbol == "BTC"
        assert result.timeframe == "1h"
        
        # Check first data point
        first_point = result[0]
        assert first_point.open == 100.0
        assert first_point.high == 105.0
        assert first_point.low == 95.0
        assert first_point.close == 102.0
        assert first_point.volume == 1000.0
        assert first_point.timestamp == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_minimal_csv_parsing(self):
        """Test parsing CSV with only required columns."""
        result = self.parser.parse(self.minimal_csv)
        
        assert isinstance(result, PriceDataFrame)
        assert len(result) == 2
        assert result.symbol == "UNKNOWN"  # Default value
        assert result.timeframe == "1h"    # Default value
    
    def test_empty_csv_validation(self):
        """Test validation of empty CSV data."""
        with pytest.raises(ValueError, match="CSV data cannot be empty"):
            self.parser.parse("")
        
        with pytest.raises(ValueError, match="CSV data cannot be empty"):
            self.parser.parse("   ")
    
    def test_missing_required_columns(self):
        """Test validation of missing required columns."""
        invalid_csv = """timestamp,open,high,low,close
2023-01-01 12:00:00,100.0,105.0,95.0,102.0"""
        
        with pytest.raises(ValueError, match="Missing required CSV columns"):
            self.parser.parse(invalid_csv)
    
    def test_invalid_price_data(self):
        """Test handling of invalid price data."""
        invalid_csv = """timestamp,open,high,low,close,volume
2023-01-01 12:00:00,invalid,105.0,95.0,102.0,1000.0"""
        
        with pytest.raises(ValueError, match="Error parsing CSV row"):
            self.parser.parse(invalid_csv)
    
    def test_invalid_timestamp(self):
        """Test handling of invalid timestamp."""
        invalid_csv = """timestamp,open,high,low,close,volume
invalid_timestamp,100.0,105.0,95.0,102.0,1000.0"""
        
        with pytest.raises(ValueError, match="Error parsing CSV row"):
            self.parser.parse(invalid_csv)
    
    def test_unix_timestamp_parsing(self):
        """Test parsing Unix timestamps."""
        unix_csv = """timestamp,open,high,low,close,volume
1672574400,100.0,105.0,95.0,102.0,1000.0
1672578000,102.0,108.0,98.0,105.0,1200.0"""
        
        result = self.parser.parse(unix_csv)
        
        assert len(result) == 2
        # Unix timestamp 1672574400 = 2023-01-01 12:00:00 UTC
        assert result[0].timestamp == datetime.fromtimestamp(1672574400)
    
    def test_unix_timestamp_milliseconds(self):
        """Test parsing Unix timestamps in milliseconds."""
        unix_ms_csv = """timestamp,open,high,low,close,volume
1672574400000,100.0,105.0,95.0,102.0,1000.0"""
        
        result = self.parser.parse(unix_ms_csv)
        
        assert len(result) == 1
        assert result[0].timestamp == datetime.fromtimestamp(1672574400)
    
    def test_iso_timestamp_parsing(self):
        """Test parsing ISO format timestamps."""
        iso_csv = """timestamp,open,high,low,close,volume
2023-01-01T12:00:00Z,100.0,105.0,95.0,102.0,1000.0
2023-01-01T13:00:00.123456Z,102.0,108.0,98.0,105.0,1200.0"""
        
        result = self.parser.parse(iso_csv)
        
        assert len(result) == 2
        assert result[0].timestamp == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_us_format_timestamp(self):
        """Test parsing US format timestamps."""
        us_csv = """timestamp,open,high,low,close,volume
01/01/2023 12:00:00,100.0,105.0,95.0,102.0,1000.0
01/01/2023,102.0,108.0,98.0,105.0,1200.0"""
        
        result = self.parser.parse(us_csv)
        
        assert len(result) == 2
        assert result[0].timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert result[1].timestamp == datetime(2023, 1, 1, 0, 0, 0)
    
    def test_validate_format_valid(self):
        """Test format validation with valid headers."""
        valid_headers = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'symbol']
        assert self.parser.validate_format(valid_headers) is True
    
    def test_validate_format_invalid(self):
        """Test format validation with invalid headers."""
        invalid_headers = ['timestamp', 'open', 'high', 'low', 'close']  # Missing volume
        assert self.parser.validate_format(invalid_headers) is False
        
        assert self.parser.validate_format(None) is False
        assert self.parser.validate_format([]) is False
    
    def test_get_sample_format(self):
        """Test sample format documentation."""
        sample = self.parser.get_sample_format()
        
        assert "timestamp,open,high,low,close,volume" in sample
        assert "Required columns:" in sample
        assert "Optional columns:" in sample
        assert "Timestamp formats supported:" in sample
    
    def test_no_valid_data_points(self):
        """Test handling when no valid data points are found."""
        # CSV with header but no data rows
        header_only_csv = """timestamp,open,high,low,close,volume"""
        
        with pytest.raises(ValueError, match="No valid data points found in CSV"):
            self.parser.parse(header_only_csv)
    
    def test_mixed_symbols_timeframes(self):
        """Test handling CSV with mixed symbols and timeframes."""
        mixed_csv = """timestamp,open,high,low,close,volume,symbol,timeframe
2023-01-01 12:00:00,100.0,105.0,95.0,102.0,1000.0,BTC,1h
2023-01-01 13:00:00,102.0,108.0,98.0,105.0,1200.0,ETH,4h"""
        
        result = self.parser.parse(mixed_csv)
        
        # Should use the last symbol/timeframe encountered
        assert result.symbol == "ETH"
        assert result.timeframe == "4h"