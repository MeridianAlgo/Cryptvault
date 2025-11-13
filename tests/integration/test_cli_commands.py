"""Integration tests for CLI commands."""

import pytest
from unittest.mock import Mock, patch
from io import StringIO


@pytest.mark.integration
@pytest.mark.cli
class TestCLICommands:
    """Test CLI command execution."""
    
    def test_cli_help_command(self):
        """Test CLI help command."""
        from cryptvault.cli.commands import show_help
        
        # Should not raise exception
        try:
            show_help()
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_cli_version_command(self):
        """Test CLI version command."""
        from cryptvault.cli.commands import show_version
        
        # Should not raise exception
        try:
            show_version()
            success = True
        except Exception:
            success = False
        
        assert success
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_analyze_command_with_mock(self, mock_stdout, sample_price_dataframe):
        """Test CLI analyze command with mocked data."""
        from cryptvault.cli.commands import analyze_ticker
        
        # This test verifies the command structure exists
        # Actual execution would require mocking the analyzer
        assert callable(analyze_ticker)


@pytest.mark.integration
@pytest.mark.cli
class TestCLIValidation:
    """Test CLI input validation."""
    
    def test_ticker_validation(self):
        """Test ticker symbol validation."""
        from cryptvault.cli.validators import validate_ticker
        
        # Valid tickers
        assert validate_ticker('BTC') is True
        assert validate_ticker('ETH') is True
        
        # Invalid tickers
        assert validate_ticker('') is False
        assert validate_ticker('INVALID123456') is False
    
    def test_interval_validation(self):
        """Test interval validation."""
        from cryptvault.cli.validators import validate_interval
        
        # Valid intervals
        assert validate_interval('1d') is True
        assert validate_interval('1h') is True
        
        # Invalid intervals
        assert validate_interval('invalid') is False
