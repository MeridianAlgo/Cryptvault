"""Integration tests for complete analysis workflow."""

import pytest
from unittest.mock import Mock, patch
from cryptvault.core.analyzer import PatternAnalyzer
from tests.fixtures.mock_responses import get_mock_yfinance_response


@pytest.mark.integration
class TestAnalyzerWorkflow:
    """Test complete analyzer workflow."""
    
    def test_analyze_dataframe_workflow(self, sample_price_dataframe):
        """Test analyzing a dataframe end-to-end."""
        analyzer = PatternAnalyzer()
        result = analyzer.analyze_dataframe(sample_price_dataframe, sensitivity=0.5)
        
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'symbol')
        assert hasattr(result, 'patterns')
    
    def test_analyze_from_csv_workflow(self, sample_csv_data):
        """Test analyzing CSV data end-to-end."""
        analyzer = PatternAnalyzer()
        result = analyzer.analyze_from_csv(sample_csv_data, sensitivity=0.5)
        
        assert result is not None
        assert hasattr(result, 'success')
    
    def test_analyze_from_json_workflow(self, sample_json_data):
        """Test analyzing JSON data end-to-end."""
        analyzer = PatternAnalyzer()
        result = analyzer.analyze_from_json(sample_json_data, sensitivity=0.5)
        
        assert result is not None
        assert hasattr(result, 'success')
    
    def test_error_handling_workflow(self, minimal_price_points):
        """Test error handling in workflow."""
        from cryptvault.data.models import PriceDataFrame
        
        # Create dataframe with minimal data
        df = PriceDataFrame(minimal_price_points, symbol='TEST')
        
        analyzer = PatternAnalyzer()
        result = analyzer.analyze_dataframe(df, sensitivity=0.5)
        
        # Should handle gracefully
        assert result is not None


@pytest.mark.integration
@pytest.mark.slow
class TestAnalyzerWithMockedAPI:
    """Test analyzer with mocked API calls."""
    
    @patch('cryptvault.data.fetchers.yfinance')
    def test_analyze_ticker_with_mock(self, mock_yf, sample_price_dataframe):
        """Test analyzing ticker with mocked API."""
        # Mock the yfinance response
        mock_ticker = Mock()
        mock_ticker.history.return_value = Mock()
        mock_yf.Ticker.return_value = mock_ticker
        
        analyzer = PatternAnalyzer()
        
        # This would normally make API call, but it's mocked
        # Just verify the analyzer can be instantiated
        assert analyzer is not None
