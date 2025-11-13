"""
Data Module

Handles all data-related operations including fetching, caching, validation,
and data model definitions.

Components:
    - models: Core data structures (PricePoint, PriceDataFrame, etc.)
    - fetchers: Data fetching from external sources
    - cache: Data caching layer
    - validators: Input validation and sanitization

Example:
    >>> from cryptvault.data import DataFetcher, DataCache
    >>> fetcher = DataFetcher()
    >>> cache = DataCache()
    >>> data = fetcher.fetch('BTC', days=60)
"""

from .models import PricePoint, PriceDataFrame

# Import other components if they exist
try:
    from .fetchers import DataFetcher
except ImportError:
    DataFetcher = None

try:
    from .cache import DataCache
except ImportError:
    DataCache = None

__all__ = [
    # Models
    'PricePoint',
    'PriceDataFrame',
]

# Add optional exports if available
if DataFetcher:
    __all__.append('DataFetcher')
if DataCache:
    __all__.append('DataCache')
