"""Package data fetcher utilities."""

from typing import Optional, Dict, Any


class PackageDataFetcher:
    """Fetch data using various packages."""

    def __init__(self):
        # Import the actual DataFetcher
        try:
            from .fetchers import DataFetcher
            self.data_fetcher = DataFetcher()
        except ImportError:
            self.data_fetcher = None

    def fetch_data(self, symbol: str, days: int = 60, interval: str = '1d') -> Optional[Dict[str, Any]]:
        """
        Fetch data for a symbol.

        Args:
            symbol: Ticker symbol
            days: Number of days of data
            interval: Data interval

        Returns:
            Dictionary with price data or None
        """
        if self.data_fetcher:
            try:
                result = self.data_fetcher.fetch(symbol, days, interval)
                if result and hasattr(result, 'data'):
                    # Convert PriceDataFrame to dict format for compatibility
                    return {
                        'data': result.data,
                        'symbol': result.symbol,
                        'timeframe': getattr(result, 'timeframe', interval)
                    }
            except Exception as e:
                import logging
                logging.error(f"Data fetch error: {e}")
        return None

    def fetch_historical_data(self, symbol: str, days: int = 60, interval: str = '1d') -> Optional[Any]:
        """
        Fetch historical data for symbol.

        Args:
            symbol: Ticker symbol
            days: Number of days of data
            interval: Data interval

        Returns:
            PriceDataFrame with historical data or None
        """
        if self.data_fetcher:
            try:
                return self.data_fetcher.fetch(symbol, days, interval)
            except Exception as e:
                import logging
                logging.error(f"Historical data fetch error: {e}")
        return None
