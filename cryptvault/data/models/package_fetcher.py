"""Fetch data from various packages (yfinance, ccxt, etc.)."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from .models import PricePoint, PriceDataFrame


logger = logging.getLogger(__name__)


class PackageDataFetcher:
    """Fetch cryptocurrency and stock data from various sources."""

    def __init__(self):
        self.yfinance_available = self._check_yfinance()
        self.ccxt_available = self._check_ccxt()

    def _check_yfinance(self) -> bool:
        """Check if yfinance is available."""
        try:
            import yfinance
            return True
        except ImportError:
            return False

    def _check_ccxt(self) -> bool:
        """Check if ccxt is available."""
        try:
            import ccxt
            return True
        except ImportError:
            return False

    def fetch_data(self, symbol: str, days: int = 30, interval: str = '1d') -> Optional[PriceDataFrame]:
        """Fetch data for symbol."""
        if self.yfinance_available:
            return self._fetch_yfinance(symbol, days, interval)
        elif self.ccxt_available:
            return self._fetch_ccxt(symbol, days, interval)
        else:
            logger.error("No data source available")
            return None

    def _fetch_yfinance(self, symbol: str, days: int, interval: str) -> Optional[PriceDataFrame]:
        """Fetch data using yfinance."""
        try:
            import yfinance as yf

            # List of crypto symbols that need -USD suffix
            crypto_symbols = [
                'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE',
                'TRX', 'DOT', 'MATIC', 'LINK', 'TON', 'SHIB', 'LTC', 'BCH', 'UNI', 'ATOM',
                'XLM', 'XMR', 'ETC', 'HBAR', 'FIL', 'APT', 'ARB', 'VET', 'NEAR', 'ALGO',
                'ICP', 'GRT', 'AAVE', 'MKR', 'SNX', 'SAND', 'MANA', 'AXS', 'FTM', 'THETA',
                'EOS', 'XTZ', 'FLOW', 'EGLD', 'ZEC', 'CAKE', 'KLAY', 'RUNE', 'NEO', 'DASH'
            ]

            # Add -USD suffix for crypto if needed
            if not any(symbol.endswith(suffix) for suffix in ['-USD', '.', '^']):
                if symbol.upper() in crypto_symbols:
                    symbol = f"{symbol}-USD"

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{days}d", interval=interval)

            if df.empty:
                return None

            data_points = []
            for index, row in df.iterrows():
                point = PricePoint(
                    timestamp=index.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                data_points.append(point)

            return PriceDataFrame(data_points, symbol=symbol, timeframe=interval)

        except Exception as e:
            logger.error(f"yfinance fetch error: {e}")
            return None

    def _fetch_ccxt(self, symbol: str, days: int, interval: str) -> Optional[PriceDataFrame]:
        """Fetch data using ccxt."""
        try:
            import ccxt

            exchange = ccxt.binance()

            # Convert symbol format
            if '/' not in symbol:
                symbol = f"{symbol}/USDT"

            # Convert interval
            timeframe_map = {'1h': '1h', '4h': '4h', '1d': '1d'}
            timeframe = timeframe_map.get(interval, '1d')

            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)

            data_points = []
            for candle in ohlcv:
                point = PricePoint(
                    timestamp=datetime.fromtimestamp(candle[0] / 1000),
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[5])
                )
                data_points.append(point)

            return PriceDataFrame(data_points, symbol=symbol, timeframe=interval)

        except Exception as e:
            logger.error(f"ccxt fetch error: {e}")
            return None

    def get_available_sources(self) -> Dict[str, bool]:
        """Get available data sources."""
        return {
            'yfinance': self.yfinance_available,
            'ccxt': self.ccxt_available
        }

    def search_tickers(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search for tickers."""
        # Comprehensive crypto list
        crypto_symbols = {
            # Top 50 Cryptocurrencies
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'USDT': 'Tether', 'BNB': 'Binance Coin',
            'SOL': 'Solana', 'XRP': 'Ripple', 'USDC': 'USD Coin', 'ADA': 'Cardano',
            'AVAX': 'Avalanche', 'DOGE': 'Dogecoin', 'TRX': 'TRON', 'DOT': 'Polkadot',
            'MATIC': 'Polygon', 'LINK': 'Chainlink', 'TON': 'Toncoin', 'SHIB': 'Shiba Inu',
            'LTC': 'Litecoin', 'BCH': 'Bitcoin Cash', 'UNI': 'Uniswap', 'ATOM': 'Cosmos',
            'XLM': 'Stellar', 'XMR': 'Monero', 'ETC': 'Ethereum Classic', 'HBAR': 'Hedera',
            'FIL': 'Filecoin', 'APT': 'Aptos', 'ARB': 'Arbitrum', 'VET': 'VeChain',
            'NEAR': 'NEAR Protocol', 'ALGO': 'Algorand', 'ICP': 'Internet Computer',
            'GRT': 'The Graph', 'AAVE': 'Aave', 'MKR': 'Maker', 'SNX': 'Synthetix',
            'SAND': 'The Sandbox', 'MANA': 'Decentraland', 'AXS': 'Axie Infinity',
            'FTM': 'Fantom', 'THETA': 'Theta Network', 'EOS': 'EOS', 'XTZ': 'Tezos',
            'FLOW': 'Flow', 'EGLD': 'MultiversX', 'ZEC': 'Zcash', 'CAKE': 'PancakeSwap',
            'KLAY': 'Klaytn', 'RUNE': 'THORChain', 'NEO': 'Neo', 'DASH': 'Dash',
            'COMP': 'Compound', 'ENJ': 'Enjin Coin', 'BAT': 'Basic Attention Token'
        }

        query_upper = query.upper()
        results = []

        for symbol, name in crypto_symbols.items():
            if query_upper in symbol or query_upper in name.upper():
                results.append({'symbol': symbol, 'name': name})
                if len(results) >= limit:
                    break

        return results

    def get_supported_tickers(self) -> List[str]:
        """Get list of supported tickers."""
        return [
            # Top Cryptocurrencies
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE',
            'TRX', 'DOT', 'MATIC', 'LINK', 'TON', 'SHIB', 'LTC', 'BCH', 'UNI', 'ATOM',
            'XLM', 'XMR', 'ETC', 'HBAR', 'FIL', 'APT', 'ARB', 'VET', 'NEAR', 'ALGO',
            'ICP', 'GRT', 'AAVE', 'MKR', 'SNX', 'SAND', 'MANA', 'AXS', 'FTM', 'THETA',
            'EOS', 'XTZ', 'FLOW', 'EGLD', 'ZEC', 'CAKE', 'KLAY', 'RUNE', 'NEO', 'DASH',
            # Popular Stocks - Tech
            'AAPL', 'TSLA', 'GOOGL', 'GOOG', 'MSFT', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD',
            'INTC', 'CRM', 'ORCL', 'ADBE', 'CSCO', 'AVGO', 'QCOM', 'TXN', 'INTU', 'IBM',
            # Stocks - Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB',
            'V', 'MA', 'PYPL', 'SQ', 'COIN',
            # Stocks - Consumer
            'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST', 'LOW', 'DIS', 'CMCSA',
            # Stocks - Healthcare
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK', 'ABT', 'DHR', 'LLY', 'BMY',
            # Stocks - Energy & Industrial
            'XOM', 'CVX', 'COP', 'SLB', 'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS',
            # Stocks - Transportation & Rideshare
            'UBER', 'LYFT', 'ABNB', 'DAL', 'UAL', 'AAL',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'GLD', 'SLV'
        ]

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol."""
        data = self.fetch_data(symbol, days=1, interval='1d')
        if data and len(data) > 0:
            return data.data[-1].close
        return None

    def validate_ticker(self, symbol: str) -> bool:
        """Validate if ticker is supported."""
        # Try to fetch minimal data to validate
        data = self.fetch_data(symbol, days=1, interval='1d')
        return data is not None

    def fetch_historical_data(self, symbol: str, days: int, interval: str) -> Optional[PriceDataFrame]:
        """Fetch historical data (alias for fetch_data)."""
        return self.fetch_data(symbol, days, interval)
