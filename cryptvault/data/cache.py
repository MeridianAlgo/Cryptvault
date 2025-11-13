"""
Data Caching

Implements caching layer for API responses to minimize external requests
and improve performance. Supports both memory and disk-based caching.

Example:
    >>> from cryptvault.data.cache import DataCache
    >>> cache = DataCache()
    >>> cache.set('BTC_60d_1d', price_data, ttl=300)
    >>> data = cache.get('BTC_60d_1d')
"""

import logging
import pickle
import hashlib
import time
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..config import get_config
from ..exceptions import CacheError

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    ttl: int
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl <= 0:
            return False
        return time.time() - self.created_at > self.ttl

    @property
    def age(self) -> float:
        """Get age in seconds."""
        return time.time() - self.created_at


class MemoryCache:
    """In-memory cache implementation."""

    def __init__(self, max_size_mb: int = 100):
        """
        Initialize memory cache.

        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size_mb = max_size_mb
        self._cache: Dict[str, CacheEntry] = {}
        self._size_bytes = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        if entry.is_expired:
            del self._cache[key]
            return None

        entry.hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache."""
        # Estimate size
        try:
            size = len(pickle.dumps(value))
        except:
            size = 1024  # Default estimate

        # Check if we need to evict
        while self._size_bytes + size > self.max_size_mb * 1024 * 1024:
            self._evict_lru()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            ttl=ttl
        )

        self._cache[key] = entry
        self._size_bytes += size

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._size_bytes = 0

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find entry with lowest hits and oldest
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].hits, -self._cache[k].created_at)
        )

        del self._cache[lru_key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = sum(e.hits for e in self._cache.values())
        return {
            'entries': len(self._cache),
            'size_mb': self._size_bytes / (1024 * 1024),
            'max_size_mb': self.max_size_mb,
            'total_hits': total_hits,
            'avg_age': sum(e.age for e in self._cache.values()) / len(self._cache) if self._cache else 0
        }


class DiskCache:
    """Disk-based cache implementation."""

    def __init__(self, cache_dir: str, max_size_mb: int = 100):
        """
        Initialize disk cache.

        Args:
            cache_dir: Directory for cache files
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.cache_dir / 'index.pkl'
        self._index: Dict[str, CacheEntry] = self._load_index()

    def _load_index(self) -> Dict[str, CacheEntry]:
        """Load cache index."""
        if self._index_file.exists():
            try:
                with open(self._index_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}

    def _save_index(self) -> None:
        """Save cache index."""
        try:
            with open(self._index_file, 'wb') as f:
                pickle.dump(self._index, f)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._index:
            return None

        entry = self._index[key]

        if entry.is_expired:
            self.delete(key)
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            del self._index[key]
            return None

        try:
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)

            entry.hits += 1
            return value

        except Exception as e:
            logger.error(f"Failed to load cache entry: {e}")
            self.delete(key)
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache."""
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)

            entry = CacheEntry(
                key=key,
                value=None,  # Don't store value in index
                created_at=time.time(),
                ttl=ttl
            )

            self._index[key] = entry
            self._save_index()

        except Exception as e:
            logger.error(f"Failed to save cache entry: {e}")
            raise CacheError(
                "Failed to save to disk cache",
                details={'key': key, 'error': str(e)},
                original_error=e
            )

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._index:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            del self._index[key]
            self._save_index()

    def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob('*.cache'):
            cache_file.unlink()
        self._index.clear()
        self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(
            self._get_cache_path(k).stat().st_size
            for k in self._index.keys()
            if self._get_cache_path(k).exists()
        )

        return {
            'entries': len(self._index),
            'size_mb': total_size / (1024 * 1024),
            'max_size_mb': self.max_size_mb,
            'total_hits': sum(e.hits for e in self._index.values())
        }


class DataCache:
    """
    Main data cache interface.

    Provides unified caching interface with automatic backend selection
    based on configuration. Supports both memory and disk caching.

    Example:
        >>> cache = DataCache()
        >>> cache.set('BTC_60d', price_data, ttl=300)
        >>> data = cache.get('BTC_60d')
        >>> if data:
        ...     print("Cache hit!")
    """

    def __init__(self):
        """Initialize data cache."""
        self.config = get_config()
        self._backend = self._initialize_backend()
        logger.info(f"Cache initialized: backend={self.config.cache.backend}")

    def _initialize_backend(self):
        """Initialize cache backend."""
        if not self.config.cache.enabled:
            return None

        if self.config.cache.backend == 'memory':
            return MemoryCache(max_size_mb=self.config.cache.max_size_mb)
        elif self.config.cache.backend == 'disk':
            cache_dir = self.config.cache.disk_path or 'cache'
            return DiskCache(cache_dir, max_size_mb=self.config.cache.max_size_mb)
        else:
            logger.warning(f"Unknown cache backend: {self.config.cache.backend}")
            return None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self._backend:
            return None

        try:
            value = self._backend.get(key)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses config default if None)
        """
        if not self._backend:
            return

        if ttl is None:
            ttl = self.config.cache.ttl

        try:
            self._backend.set(key, value, ttl)
            logger.debug(f"Cache set: {key} (ttl={ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if not self._backend:
            return

        try:
            self._backend.delete(key)
            logger.debug(f"Cache delete: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def clear(self) -> None:
        """Clear all cache entries."""
        if not self._backend:
            return

        try:
            self._backend.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self._backend:
            return {'enabled': False}

        try:
            stats = self._backend.get_stats()
            stats['enabled'] = True
            stats['backend'] = self.config.cache.backend
            return stats
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'enabled': True, 'error': str(e)}

    @staticmethod
    def make_key(symbol: str, days: int, interval: str) -> str:
        """
        Create cache key from parameters.

        Args:
            symbol: Ticker symbol
            days: Number of days
            interval: Data interval

        Returns:
            Cache key string
        """
        return f"{symbol}_{days}d_{interval}"
