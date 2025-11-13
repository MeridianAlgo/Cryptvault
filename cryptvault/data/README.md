# Data Module

This module handles all data-related operations for CryptVault.

## Components

- **models.py**: Core data structures (PricePoint, PriceDataFrame, TickerInfo, MarketData)
- **fetchers.py**: Data fetching from external sources (yfinance, ccxt, cryptocompare)
- **cache.py**: Data caching layer with 5-minute TTL
- **validators.py**: Input validation and sanitization

## Purpose

The data module provides:
- Unified interface for fetching market data from multiple sources
- Structured data models for price and market information
- Caching to reduce API calls and improve performance
- Validation to ensure data integrity and security

## Usage

```python
from cryptvault.data import DataFetcher, DataCache, validate_ticker_symbol

# Validate input
if validate_ticker_symbol('BTC'):
    # Fetch data with caching
    fetcher = DataFetcher()
    cache = DataCache()
    
    # Check cache first
    cached_data = cache.get('BTC', days=60)
    if not cached_data:
        data = fetcher.fetch('BTC', days=60)
        cache.set('BTC', data, days=60)
```
