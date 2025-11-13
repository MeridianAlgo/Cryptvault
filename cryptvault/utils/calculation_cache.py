"""
Calculation Caching Utilities

This module provides caching mechanisms for expensive calculations to improve
performance by avoiding redundant computations.

Features:
- LRU cache for function results
- Hash-based cache keys for data arrays
- TTL-based cache expiration
- Memory-efficient storage

Example:
    >>> from cryptvault.utils.calculation_cache import cached_calculation
    >>> @cached_calculation(ttl=300)
    ... def expensive_calculation(data):
    ...     return complex_computation(data)
"""

import hashlib
import time
import functools
import numpy as np
from typing import Any, Callable, Dict, Optional, Tuple
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class CalculationCache:
    """
    LRU cache for expensive calculations with TTL support.

    This cache stores calculation results with automatic expiration and
    size limits to prevent memory bloat.

    Attributes:
        max_size: Maximum number of cached items
        default_ttl: Default time-to-live in seconds
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize calculation cache.

        Args:
            max_size: Maximum cache size (default: 1000 items)
            default_ttl: Default TTL in seconds (default: 300s / 5min)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None

        # Check expiration
        if key in self._timestamps:
            age = time.time() - self._timestamps[key]
            if age > self.default_ttl:
                # Expired
                del self._cache[key]
                del self._timestamps[key]
                self._misses += 1
                return None

        # Move to end (LRU)
        self._cache.move_to_end(key)
        self._hits += 1
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override
        """
        # Remove oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._timestamps:
                del self._timestamps[oldest_key]

        self._cache[key] = value
        self._cache.move_to_end(key)
        self._timestamps[key] = time.time()

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._timestamps.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


# Global cache instance
_global_cache = CalculationCache(max_size=1000, default_ttl=300)


def get_cache() -> CalculationCache:
    """Get the global calculation cache."""
    return _global_cache


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments.

    This function creates a deterministic hash from function arguments,
    handling NumPy arrays and other data types appropriately.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    key_parts = []

    # Process positional arguments
    for arg in args:
        if isinstance(arg, np.ndarray):
            # Hash array data
            key_parts.append(hashlib.md5(arg.tobytes()).hexdigest()[:16])
        elif isinstance(arg, (list, tuple)):
            # Convert to array and hash
            arr = np.array(arg)
            key_parts.append(hashlib.md5(arr.tobytes()).hexdigest()[:16])
        else:
            # Use string representation
            key_parts.append(str(arg))

    # Process keyword arguments
    for k, v in sorted(kwargs.items()):
        if isinstance(v, np.ndarray):
            key_parts.append(f"{k}={hashlib.md5(v.tobytes()).hexdigest()[:16]}")
        elif isinstance(v, (list, tuple)):
            arr = np.array(v)
            key_parts.append(f"{k}={hashlib.md5(arr.tobytes()).hexdigest()[:16]}")
        else:
            key_parts.append(f"{k}={v}")

    return "|".join(key_parts)


def cached_calculation(ttl: Optional[int] = None, cache_instance: Optional[CalculationCache] = None):
    """
    Decorator to cache expensive calculation results.

    This decorator caches function results based on input arguments,
    avoiding redundant calculations for the same inputs.

    Args:
        ttl: Time-to-live in seconds (None uses cache default)
        cache_instance: Optional cache instance (uses global if None)

    Returns:
        Decorated function with caching

    Example:
        >>> @cached_calculation(ttl=300)
        ... def calculate_indicators(prices, period):
        ...     # expensive calculation
        ...     return result
    """
    cache = cache_instance or _global_cache

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            arg_key = generate_cache_key(*args, **kwargs)
            cache_key = f"{func_name}:{arg_key}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func_name}")
                return cached_result

            # Calculate and cache
            logger.debug(f"Cache miss for {func_name}, calculating...")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)

            return result

        # Add cache control methods
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.get_cache_stats = lambda: cache.get_stats()

        return wrapper

    return decorator


def memoize_last_n(n: int = 10):
    """
    Decorator to memoize last N function calls.

    This is a lightweight alternative to full caching for functions
    that are often called with the same recent arguments.

    Args:
        n: Number of recent calls to cache

    Returns:
        Decorated function with memoization

    Example:
        >>> @memoize_last_n(n=5)
        ... def get_data(symbol):
        ...     return fetch_data(symbol)
    """
    def decorator(func: Callable) -> Callable:
        cache = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = generate_cache_key(*args, **kwargs)

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = func(*args, **kwargs)

            cache[key] = result
            cache.move_to_end(key)

            # Remove oldest if over limit
            if len(cache) > n:
                cache.popitem(last=False)

            return result

        return wrapper

    return decorator


class BatchCalculator:
    """
    Utility for batching calculations to reduce overhead.

    This class allows accumulating calculation requests and processing
    them in batches for improved efficiency.

    Example:
        >>> calculator = BatchCalculator()
        >>> calculator.add_calculation(calculate_sma, prices1, 20)
        >>> calculator.add_calculation(calculate_sma, prices2, 20)
        >>> results = calculator.execute_batch()
    """

    def __init__(self):
        """Initialize batch calculator."""
        self.calculations = []

    def add_calculation(self, func: Callable, *args, **kwargs) -> int:
        """
        Add calculation to batch.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Index of calculation in batch
        """
        self.calculations.append((func, args, kwargs))
        return len(self.calculations) - 1

    def execute_batch(self) -> list:
        """
        Execute all batched calculations.

        Returns:
            List of results in order added
        """
        results = []

        for func, args, kwargs in self.calculations:
            try:
                result = func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch calculation failed: {e}")
                results.append(None)

        self.calculations.clear()
        return results

    def clear(self) -> None:
        """Clear all pending calculations."""
        self.calculations.clear()


def reduce_precision(arr: np.ndarray, decimals: int = 4) -> np.ndarray:
    """
    Reduce array precision to save memory and improve cache efficiency.

    Args:
        arr: NumPy array
        decimals: Number of decimal places

    Returns:
        Array with reduced precision
    """
    return np.round(arr, decimals=decimals)


def deduplicate_calculations(calculations: list) -> Tuple[list, Dict[int, int]]:
    """
    Identify and remove duplicate calculations.

    Args:
        calculations: List of (func, args, kwargs) tuples

    Returns:
        Tuple of (unique_calculations, index_mapping)
        where index_mapping maps original indices to unique indices
    """
    unique_calcs = []
    calc_keys = {}
    index_mapping = {}

    for i, (func, args, kwargs) in enumerate(calculations):
        key = generate_cache_key(func.__name__, *args, **kwargs)

        if key in calc_keys:
            # Duplicate found
            index_mapping[i] = calc_keys[key]
        else:
            # New unique calculation
            unique_idx = len(unique_calcs)
            unique_calcs.append((func, args, kwargs))
            calc_keys[key] = unique_idx
            index_mapping[i] = unique_idx

    return unique_calcs, index_mapping
