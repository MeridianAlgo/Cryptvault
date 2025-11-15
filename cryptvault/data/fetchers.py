"""
Data Fetchers

Unified interface for fetching market data from multiple sources including
yfinance, CCXT (cryptocurrency exchanges), and CryptoCompare.

Example:
    >>> from cryptvault.data.fetchers import DataFetcher
    >>> fetcher = DataFetcher()
    >>> data = fetcher.fetch('BTC', days=60, interval='1d')
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import time

from . import models
from .models import PricePoint
from .models import PriceDataFrame as PriceDataFrameMain
try:
    from ..models import TickerInfo, MarketData
except ImportError:
    # TickerInfo and MarketData may not be available
    TickerInfo = None
    MarketData = None
from ..exceptions import (
    DataFetchError, APIError, NetworkError, RateLimitError,
    InvalidTickerError, InsufficientDataError
)
from ..config.manager import ConfigManager

logger = logging.getLogger(__name__)


class BaseDataFetcher(ABC):
    """
    Abstract base class for data fetchers.

    All data fetchers must implement the fetch method to retrieve
    price data from their respective sources.
    """

    def __init__(self) -> None:
        """Initialize base fetcher."""
        self.config = ConfigManager()
        self.last_request_time = 0
        self.request_count = 0

    @abstractmethod
    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> PriceDataFrameMain:
        """
        Fetch price data for symbol.

        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            PriceDataFrameMain with fetched data

        Raises:
            DataFetchError: If fetch fails
        """
        pass

    @abstractmethod
    def get_ticker_info(self, symbol: str) -> TickerInfo:
        """
        Get ticker information.

        Args:
            symbol: Ticker symbol

        Returns:
            TickerInfo object
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if data source is available."""
        pass

    def _rate_limit(self) -> None:
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < 1.0:  # Minimum 1 second between requests
            time.sleep(1.0 - time_since_last)

        self.last_request_time = time.time()
        self.request_count += 1


class YFinanceFetcher(BaseDataFetcher):
    """Fetch data from Yahoo Finance using yfinance library."""

    def __init__(self) -> None:
        """Initialize yfinance fetcher."""
        super().__init__()
        self._yfinance = None

    def _get_yfinance(self):
        """Lazy load yfinance."""
        if self._yfinance is None:
            try:
                import yfinance as yf
                self._yfinance = yf
            except ImportError:
                raise DataFetchError(
                    "yfinance not installed",
                    details={'install': 'pip install yfinance'}
                )
        return self._yfinance

    def is_available(self) -> bool:
        """Check if yfinance is available."""
        try:
            self._get_yfinance()
            return True
        except:
            return False

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> PriceDataFrameMain:
        """Fetch data from Yahoo Finance."""
        self._rate_limit()

        try:
            yf = self._get_yfinance()
            ticker = yf.Ticker(symbol)

            # Download data
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if df.empty:
                raise InsufficientDataError(
                    f"No data available for {symbol}",
                    details={'symbol': symbol, 'start': start_date, 'end': end_date}
                )

            # Convert to PricePoint list
            price_points = []
            for index, row in df.iterrows():
                point = PricePoint(
                    timestamp=index.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                price_points.append(point)

            return PriceDataFrameMain(price_points, symbol=symbol, timeframe=interval)

        except Exception as e:
            logger.error(f"YFinance fetch failed: {e}", exc_info=True)
            raise DataFetchError(
                f"Failed to fetch data from Yahoo Finance",
                details={'symbol': symbol, 'error': str(e)},
                original_error=e
            )

    def get_ticker_info(self, symbol: str) -> TickerInfo:
        """Get ticker info from Yahoo Finance."""
        try:
            yf = self._get_yfinance()
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return TickerInfo(
                symbol=symbol,
                name=info.get('longName', symbol),
                type='stock' if 'stock' in info.get('quoteType', '').lower() else 'crypto',
                exchange=info.get('exchange', 'Unknown'),
                currency=info.get('currency', 'USD'),
                market_cap=info.get('marketCap'),
                description=info.get('longBusinessSummary')
            )
        except Exception as e:
            logger.warning(f"Failed to get ticker info: {e}")
            return TickerInfo(
                symbol=symbol,
                name=symbol,
                type='unknown',
                exchange='Unknown',
                currency='USD'
            )


class CCXTFetcher(BaseDataFetcher):
    """Fetch data from cryptocurrency exchanges using CCXT."""

    def __init__(self, exchange_id: str = 'binance') -> None:
        """Initialize CCXT fetcher."""
        super().__init__()
        self.exchange_id = exchange_id
        self._ccxt = None
        self._exchange = None

    def _get_ccxt(self):
        """Lazy load CCXT."""
        if self._ccxt is None:
            try:
                import ccxt
                self._ccxt = ccxt
                exchange_class = getattr(ccxt, self.exchange_id)
                self._exchange = exchange_class()
            except ImportError:
                raise DataFetchError(
                    "ccxt not installed",
                    details={'install': 'pip install ccxt'}
                )
        return self._ccxt

    def is_available(self) -> bool:
        """Check if CCXT is available."""
        try:
            self._get_ccxt()
            return True
        except:
            return False

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> PriceDataFrameMain:
        """Fetch data from cryptocurrency exchange."""
        self._rate_limit()

        try:
            self._get_ccxt()

            # Convert symbol format (BTC -> BTC/USDT)
            if '/' not in symbol:
                symbol = f"{symbol}/USDT"

            # Convert interval
            timeframe_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '4h': '4h', '1d': '1d', '1wk': '1w'
            }
            timeframe = timeframe_map.get(interval, '1d')

            # Fetch OHLCV data
            since = int(start_date.timestamp() * 1000)
            ohlcv = self._exchange.fetch_ohlcv(symbol, timeframe, since)

            if not ohlcv:
                raise InsufficientDataError(
                    f"No data available for {symbol}",
                    details={'symbol': symbol, 'exchange': self.exchange_id}
                )

            # Convert to PricePoint list
            price_points = []
            for candle in ohlcv:
                timestamp, open_price, high, low, close, volume = candle
                point = PricePoint(
                    timestamp=datetime.fromtimestamp(timestamp / 1000),
                    open=float(open_price),
                    high=float(high),
                    low=float(low),
                    close=float(close),
                    volume=float(volume)
                )
                price_points.append(point)

            return PriceDataFrameMain(price_points, symbol=symbol.split('/')[0], timeframe=interval)

        except Exception as e:
            logger.error(f"CCXT fetch failed: {e}", exc_info=True)
            raise DataFetchError(
                f"Failed to fetch data from {self.exchange_id}",
                details={'symbol': symbol, 'error': str(e)},
                original_error=e
            )

    def get_ticker_info(self, symbol: str) -> TickerInfo:
        """Get ticker info from exchange."""
        return TickerInfo(
            symbol=symbol,
            name=symbol,
            type='crypto',
            exchange=self.exchange_id,
            currency='USDT'
        )


class DataFetcher:
    """
    Unified data fetcher with automatic fallback.

    Attempts to fetch data from primary source, falls back to alternatives
    if primary fails. Implements retry logic and error handling.

    Example:
        >>> fetcher = DataFetcher()
        >>> data = fetcher.fetch('BTC', days=60)
        >>> market_data = fetcher.fetch_market_data('AAPL', days=30)
    """

    def __init__(self) -> None:
        """Initialize unified data fetcher."""
        self.config = ConfigManager()
        self.fetchers: Dict[str, BaseDataFetcher] = {}
        self._initialize_fetchers()

    def _initialize_fetchers(self) -> None:
        """Initialize available fetchers."""
        # Check if config has data_sources attribute, otherwise use defaults
        has_data_sources = hasattr(self.config, 'data_sources')
        
        # YFinance
        yfinance_enabled = getattr(self.config.data_sources, 'yfinance_enabled', True) if has_data_sources else True
        if yfinance_enabled:
            try:
                self.fetchers['yfinance'] = YFinanceFetcher()
                if self.fetchers['yfinance'].is_available():
                    logger.info("YFinance fetcher initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize YFinance: {e}")

        # CCXT
        ccxt_enabled = getattr(self.config.data_sources, 'ccxt_enabled', True) if has_data_sources else True
        if ccxt_enabled:
            try:
                self.fetchers['ccxt'] = CCXTFetcher()
                if self.fetchers['ccxt'].is_available():
                    logger.info("CCXT fetcher initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize CCXT: {e}")

    def fetch(
        self,
        symbol: str,
        days: int = 60,
        interval: str = '1d',
        source: Optional[str] = None
    ) -> PriceDataFrameMain:
        """
        Fetch price data with automatic fallback.

        Args:
            symbol: Ticker symbol
            days: Number of days of data
            interval: Data interval
            source: Specific source to use (optional)

        Returns:
            PriceDataFrameMain with fetched data

        Raises:
            DataFetchError: If all sources fail

        Example:
            >>> fetcher = DataFetcher()
            >>> data = fetcher.fetch('BTC', days=60, interval='1d')
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Determine sources to try
        if source:
            sources = [source]
        else:
            # Check if CCXT is enabled via environment variable
            if os.getenv('CRYPTVAULT_ENABLE_CCXT'):
                # Get sources from config or use defaults
                if hasattr(self.config, 'data_sources') and hasattr(self.config.data_sources, 'primary'):
                    sources = [self.config.data_sources.primary] + getattr(self.config.data_sources, 'fallback', ['yfinance'])
                else:
                    # Default: try yfinance first, then ccxt
                    sources = ['yfinance', 'ccxt']
            else:
                # Only use YFinance
                sources = ['yfinance']

        last_error = None
        for source_name in sources:
            if source_name not in self.fetchers:
                continue

            fetcher = self.fetchers[source_name]

            try:
                logger.info(f"Fetching {symbol} from {source_name}")
                data = fetcher.fetch(symbol, start_date, end_date, interval)
                logger.info(f"Successfully fetched {len(data)} points from {source_name}")
                return data

            except Exception as e:
                logger.warning(f"Failed to fetch from {source_name}: {e}")
                last_error = e
                continue

        # All sources failed
        raise DataFetchError(
            f"Failed to fetch data for {symbol} from all sources",
            details={
                'symbol': symbol,
                'sources_tried': sources,
                'last_error': str(last_error)
            },
            original_error=last_error
        )

    def fetch_market_data(
        self,
        symbol: str,
        days: int = 60,
        interval: str = '1d'
    ) -> MarketData:
        """
        Fetch complete market data including ticker info.

        Args:
            symbol: Ticker symbol
            days: Number of days
            interval: Data interval

        Returns:
            MarketData object
        """
        price_data = self.fetch(symbol, days, interval)

        # Get ticker info from primary source
        ticker_info = None
        if hasattr(self.config, 'data_sources') and hasattr(self.config.data_sources, 'primary'):
            sources_to_try = [self.config.data_sources.primary] + getattr(self.config.data_sources, 'fallback', ['yfinance'])
        else:
            sources_to_try = ['yfinance', 'ccxt']
        
        for source_name in sources_to_try:
            if source_name in self.fetchers:
                try:
                    ticker_info = self.fetchers[source_name].get_ticker_info(symbol)
                    break
                except:
                    continue

        if not ticker_info:
            ticker_info = TickerInfo(
                symbol=symbol,
                name=symbol,
                type='unknown',
                exchange='Unknown',
                currency='USD'
            )

        return MarketData(
            price_data=price_data,
            ticker_info=ticker_info,
            fetch_time=datetime.now(),
            source=getattr(self.config.data_sources, 'primary', 'yfinance') if hasattr(self.config, 'data_sources') else 'yfinance'
        )

    def get_available_sources(self) -> Dict[str, bool]:
        """
        Get status of available data sources.

        Returns:
            Dictionary mapping source names to availability
        """
        return {
            name: fetcher.is_available()
            for name, fetcher in self.fetchers.items()
        }
