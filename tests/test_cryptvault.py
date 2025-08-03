"""
Basic tests for CryptVault functionality
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import cryptvault
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    """Test that we can import the main module"""
    try:
        import cryptvault
        assert True
    except ImportError:
        # If cryptvault.py doesn't exist as a module, try importing the analyzer
        from cryptvault.analyzer import PatternAnalyzer
        assert PatternAnalyzer is not None

def test_pattern_analyzer_init():
    """Test that PatternAnalyzer can be initialized"""
    from cryptvault.analyzer import PatternAnalyzer
    analyzer = PatternAnalyzer()
    assert analyzer is not None

def test_supported_tickers():
    """Test that we can get supported tickers"""
    from cryptvault.analyzer import PatternAnalyzer
    analyzer = PatternAnalyzer()
    tickers = analyzer.get_supported_tickers()
    assert isinstance(tickers, list)
    assert len(tickers) > 0
    assert 'BTC' in tickers

def test_search_tickers():
    """Test ticker search functionality"""
    from cryptvault.analyzer import PatternAnalyzer
    analyzer = PatternAnalyzer()
    results = analyzer.search_tickers("bitcoin", limit=5)
    assert isinstance(results, list)
    # Should find at least one result for bitcoin
    assert len(results) >= 1

def test_data_sources():
    """Test that data sources are available"""
    from cryptvault.data.package_fetcher import PackageDataFetcher
    fetcher = PackageDataFetcher()
    sources = fetcher.get_available_sources()
    assert isinstance(sources, dict)
    # Should have at least one data source available
    assert any(sources.values())

def test_pattern_library():
    """Test that pattern library is properly loaded"""
    # This would test the advanced crypto charts if available
    try:
        from advanced_crypto_charts import AdvancedCryptoCharts
        charts = AdvancedCryptoCharts()
        assert len(charts.patterns) > 10  # Should have many patterns
    except ImportError:
        # Skip if advanced charts not available
        pass

def test_ml_models():
    """Test that ML models can be imported"""
    from cryptvault.ml.models.ensemble_model import AdvancedEnsembleModel
    model = AdvancedEnsembleModel()
    assert model is not None
    assert hasattr(model, 'models')
    assert len(model.models) > 0

def test_requirements():
    """Test that required packages are available"""
    import numpy
    import pandas
    import sklearn
    assert numpy is not None
    assert pandas is not None
    assert sklearn is not None

if __name__ == "__main__":
    pytest.main([__file__])