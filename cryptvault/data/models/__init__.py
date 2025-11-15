"""Data handling module for CryptVault."""

from .models import PricePoint, PriceDataFrame
# TickerInfo and MarketData are in parent models.py, not models/models.py
try:
    from ..models import TickerInfo, MarketData
except ImportError:
    # Fallback if not available
    TickerInfo = None
    MarketData = None

from .parsers import CSVParser, JSONParser
from .validator import DataValidator
from .package_fetcher import PackageDataFetcher

__all__ = [
    "PricePoint",
    "PriceDataFrame",
    "CSVParser",
    "JSONParser",
    "DataValidator",
    "PackageDataFetcher",
]

# Add TickerInfo and MarketData if available
if TickerInfo is not None:
    __all__.append("TickerInfo")
if MarketData is not None:
    __all__.append("MarketData")
