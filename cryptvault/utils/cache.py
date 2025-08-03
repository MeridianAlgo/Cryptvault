"""Intelligent caching system for CryptVault data and analysis results."""

import json
import pickle
import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union
import logging


class CacheManager:
    """Intelligent caching system with TTL and compression."""
    
    def __init__(self, cache_dir: str = ".cryptvault_cache", default_ttl: int = 300):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl  # 5 minutes default
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for key."""
        # Create hash of key for filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def _is_expired(self, cache_data: Dict) -> bool:
        """Check if cache entry is expired."""
        if 'expires_at' not in cache_data:
            return True
        
        expires_at = datetime.fromisoformat(cache_data['expires_at'])
        return datetime.now() > expires_at
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            cache_path = self._get_cache_path(key)
            
            if not os.path.exists(cache_path):
                self.stats['misses'] += 1
                return None
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            if self._is_expired(cache_data):
                self._delete_cache_file(cache_path)
                self.stats['misses'] += 1
                self.stats['evictions'] += 1
                return None
            
            self.stats['hits'] += 1
            return cache_data['value']
        
        except Exception as e:
            self.logger.warning(f"Cache get error for key {key}: {e}")
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        try:
            cache_path = self._get_cache_path(key)
            ttl = ttl or self.default_ttl
            
            cache_data = {
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                'key': key
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.stats['sets'] += 1
            return True
        
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def _delete_cache_file(self, cache_path: str):
        """Delete cache file."""
        try:
            os.remove(cache_path)
        except Exception as e:
            self.logger.warning(f"Failed to delete cache file {cache_path}: {e}")
    
    def clear(self) -> int:
        """Clear all cache entries."""
        cleared = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    os.remove(cache_path)
                    cleared += 1
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
        
        return cleared
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        cleaned = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(cache_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        if self._is_expired(cache_data):
                            os.remove(cache_path)
                            cleaned += 1
                            self.stats['evictions'] += 1
                    
                    except Exception:
                        # Remove corrupted cache files
                        os.remove(cache_path)
                        cleaned += 1
        
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")
        
        return cleaned
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Get cache size
        cache_size = 0
        cache_files = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    cache_size += os.path.getsize(cache_path)
                    cache_files += 1
        except Exception:
            pass
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.1f}%",
            'cache_files': cache_files,
            'cache_size_mb': cache_size / (1024 * 1024),
            'cache_dir': self.cache_dir
        }
    
    def cache_key_for_analysis(self, ticker: str, days: int, interval: str, 
                              sensitivity: float = 0.5) -> str:
        """Generate cache key for analysis results."""
        return f"analysis:{ticker}:{days}:{interval}:{sensitivity}"
    
    def cache_key_for_data(self, ticker: str, days: int, interval: str) -> str:
        """Generate cache key for price data."""
        return f"data:{ticker}:{days}:{interval}"
    
    def cache_key_for_price(self, ticker: str) -> str:
        """Generate cache key for current price."""
        return f"price:{ticker}"


# Global cache instance
cache = CacheManager()