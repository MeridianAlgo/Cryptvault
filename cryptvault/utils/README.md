# Utils Module

This module provides common utility functions used throughout CryptVault.

## Components

- **logging.py**: Logging configuration and utilities with rotation support
- **decorators.py**: Common decorators (retry, cache, timing, error handling)
- **helpers.py**: General helper functions

## Purpose

The utils module provides:
- Centralized logging configuration
- Reusable decorators for common patterns
- Helper functions for data manipulation
- Performance monitoring utilities
- Error handling utilities

## Usage

```python
from cryptvault.utils.decorators import retry, timing, cache
from cryptvault.utils.logging import get_logger

# Get logger
logger = get_logger(__name__)

# Use decorators
@retry(max_attempts=3, backoff=2.0)
@timing
@cache(ttl=300)
def fetch_data(symbol):
    logger.info(f"Fetching data for {symbol}")
    # ... fetch logic
    return data
```
