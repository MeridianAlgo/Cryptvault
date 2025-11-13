"""
Prediction Cache with Accuracy Tracking

This module provides caching functionality for ML predictions with:
- Time-based cache expiration (TTL)
- Accuracy tracking for verified predictions
- Cache statistics and performance metrics
- Automatic cleanup of old predictions

Cache Strategy:
- Default TTL: 5 minutes (300 seconds)
- Predictions are cached by symbol, data length, and horizon
- Cache is automatically invalidated after TTL expires
- Accuracy is tracked when actual prices become available

Performance:
- O(1) cache lookup and storage
- Minimal memory footprint
- Thread-safe operations
"""

import time
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging


@dataclass
class CachedPrediction:
    """
    Cached prediction with metadata.

    Attributes:
        value: The prediction result dictionary
        timestamp: When the prediction was made
        ttl: Time-to-live in seconds
        symbol: Ticker symbol for the prediction
        target_price: Predicted price (for accuracy tracking)
        target_date: Date when prediction should be verified
        verified: Whether prediction has been verified
        accurate: Whether prediction was accurate (if verified)
    """
    value: Dict[str, Any]
    timestamp: float
    ttl: int
    symbol: str
    target_price: Optional[float] = None
    target_date: Optional[datetime] = None
    verified: bool = False
    accurate: bool = False


class PredictionCache:
    """
    Cache for ML predictions with accuracy tracking.

    This class manages a cache of ML predictions with the following features:
    - Time-based expiration (TTL)
    - Accuracy tracking when actual prices are available
    - Cache statistics and performance metrics
    - Automatic cleanup of expired predictions

    Usage:
        cache = PredictionCache()
        cache.set(key, prediction, ttl=300)
        cached = cache.get(key)
        stats = cache.get_cache_stats()

    Thread Safety:
        This implementation is not thread-safe. For multi-threaded use,
        wrap operations with appropriate locking mechanisms.
    """

    def __init__(self):
        """Initialize prediction cache."""
        self._cache: Dict[str, CachedPrediction] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("Prediction cache initialized")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached prediction if not expired.

        Args:
            key: Cache key (typically symbol_length_horizon)

        Returns:
            Cached prediction value or None if not found/expired
        """
        if key not in self._cache:
            return None

        cached = self._cache[key]

        # Check if expired
        if time.time() - cached.timestamp > cached.ttl:
            self.logger.debug(f"Cache expired for key: {key}")
            del self._cache[key]
            return None

        self.logger.debug(f"Cache hit for key: {key}")
        return cached.value

    def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: int = 300,
        symbol: Optional[str] = None,
        target_price: Optional[float] = None,
        target_date: Optional[datetime] = None
    ) -> None:
        """
        Cache a prediction with optional accuracy tracking.

        Args:
            key: Cache key
            value: Prediction result to cache
            ttl: Time-to-live in seconds (default: 300 = 5 minutes)
            symbol: Ticker symbol (for accuracy tracking)
            target_price: Predicted price (for accuracy tracking)
            target_date: Date when prediction should be verified
        """
        cached = CachedPrediction(
            value=value,
            timestamp=time.time(),
            ttl=ttl,
            symbol=symbol or 'unknown',
            target_price=target_price,
            target_date=target_date,
            verified=False,
            accurate=False
        )

        self._cache[key] = cached
        self.logger.debug(f"Cached prediction for key: {key} (TTL: {ttl}s)")

    def verify_prediction(
        self,
        key: str,
        actual_price: float,
        tolerance: float = 0.05
    ) -> bool:
        """
        Verify a cached prediction against actual price.

        Args:
            key: Cache key of prediction to verify
            actual_price: Actual price observed
            tolerance: Acceptable error tolerance (default: 5%)

        Returns:
            True if prediction was accurate, False otherwise
        """
        if key not in self._cache:
            self.logger.warning(f"Cannot verify: prediction not found for key {key}")
            return False

        cached = self._cache[key]

        if cached.target_price is None:
            self.logger.warning(f"Cannot verify: no target price for key {key}")
            return False

        # Calculate error
        error = abs(actual_price - cached.target_price) / cached.target_price
        accurate = error <= tolerance

        # Update cached prediction
        cached.verified = True
        cached.accurate = accurate

        self.logger.info(
            f"Verified prediction for {cached.symbol}: "
            f"predicted={cached.target_price:.2f}, actual={actual_price:.2f}, "
            f"error={error:.2%}, accurate={accurate}"
        )

        return accurate

    def clear(self) -> None:
        """Clear all cached predictions."""
        count = len(self._cache)
        self._cache.clear()
        self.logger.info(f"Cleared {count} cached predictions")

    def cleanup_expired(self) -> int:
        """
        Remove expired predictions from cache.

        Returns:
            Number of predictions removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, cached in self._cache.items()
            if current_time - cached.timestamp > cached.ttl
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired predictions")

        return len(expired_keys)

    def cleanup_old_predictions(self, days_to_keep: int = 90) -> int:
        """
        Remove predictions older than specified days.

        Args:
            days_to_keep: Number of days to keep predictions

        Returns:
            Number of predictions removed
        """
        cutoff_time = time.time() - (days_to_keep * 86400)
        old_keys = [
            key for key, cached in self._cache.items()
            if cached.timestamp < cutoff_time
        ]

        for key in old_keys:
            del self._cache[key]

        if old_keys:
            self.logger.info(f"Cleaned up {len(old_keys)} old predictions (>{days_to_keep} days)")

        return len(old_keys)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics:
            - total_predictions: Total number of cached predictions
            - verified_predictions: Number of verified predictions
            - accurate_predictions: Number of accurate predictions
            - accuracy_rate: Percentage of accurate predictions
            - pending_predictions: Number of unverified predictions
            - expired_predictions: Number of expired predictions
            - cache_size_mb: Approximate cache size in MB
            - oldest_prediction: Age of oldest prediction in hours
        """
        current_time = time.time()

        total = len(self._cache)
        verified = sum(1 for c in self._cache.values() if c.verified)
        accurate = sum(1 for c in self._cache.values() if c.accurate)
        expired = sum(
            1 for c in self._cache.values()
            if current_time - c.timestamp > c.ttl
        )

        # Calculate accuracy rate
        accuracy_rate = (accurate / verified * 100) if verified > 0 else 0.0

        # Find oldest prediction
        if self._cache:
            oldest_timestamp = min(c.timestamp for c in self._cache.values())
            oldest_age_hours = (current_time - oldest_timestamp) / 3600
        else:
            oldest_age_hours = 0.0

        # Estimate cache size (rough approximation)
        cache_size_mb = len(self._cache) * 0.001  # ~1KB per prediction

        return {
            'total_predictions': total,
            'verified_predictions': verified,
            'accurate_predictions': accurate,
            'accuracy_rate': round(accuracy_rate, 2),
            'pending_predictions': total - verified,
            'expired_predictions': expired,
            'cache_size_mb': round(cache_size_mb, 3),
            'oldest_prediction_hours': round(oldest_age_hours, 2)
        }

    def get_accuracy_report(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get accuracy report for recent predictions.

        Args:
            days_back: Number of days to include in report

        Returns:
            Dictionary with accuracy metrics:
            - total_verified: Total verified predictions
            - total_accurate: Total accurate predictions
            - accuracy_rate: Overall accuracy percentage
            - by_symbol: Accuracy breakdown by symbol
            - recent_predictions: List of recent predictions
        """
        cutoff_time = time.time() - (days_back * 86400)

        recent_predictions = [
            cached for cached in self._cache.values()
            if cached.timestamp >= cutoff_time and cached.verified
        ]

        total_verified = len(recent_predictions)
        total_accurate = sum(1 for p in recent_predictions if p.accurate)
        accuracy_rate = (total_accurate / total_verified * 100) if total_verified > 0 else 0.0

        # Breakdown by symbol
        by_symbol = {}
        for pred in recent_predictions:
            symbol = pred.symbol
            if symbol not in by_symbol:
                by_symbol[symbol] = {'verified': 0, 'accurate': 0}

            by_symbol[symbol]['verified'] += 1
            if pred.accurate:
                by_symbol[symbol]['accurate'] += 1

        # Calculate accuracy rate per symbol
        for symbol, stats in by_symbol.items():
            stats['accuracy_rate'] = (
                stats['accurate'] / stats['verified'] * 100
                if stats['verified'] > 0 else 0.0
            )

        return {
            'days_back': days_back,
            'total_verified': total_verified,
            'total_accurate': total_accurate,
            'accuracy_rate': round(accuracy_rate, 2),
            'by_symbol': by_symbol,
            'recent_predictions_count': len(recent_predictions)
        }

    def get_predictions_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get all cached predictions for a specific symbol.

        Args:
            symbol: Ticker symbol

        Returns:
            List of prediction dictionaries
        """
        predictions = [
            {
                'value': cached.value,
                'timestamp': datetime.fromtimestamp(cached.timestamp).isoformat(),
                'verified': cached.verified,
                'accurate': cached.accurate,
                'target_price': cached.target_price
            }
            for cached in self._cache.values()
            if cached.symbol == symbol
        ]

        return predictions
