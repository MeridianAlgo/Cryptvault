"""
Rate Limiting

Implements rate limiting for API calls with exponential backoff and
configurable limits to prevent API abuse and respect external API limits.

Example:
    >>> from cryptvault.security import RateLimiter, rate_limit
    >>> limiter = RateLimiter(max_calls=100, period=60)
    >>> limiter.acquire('api_call')
    
    >>> @rate_limit(max_calls=10, period=60)
    ... def my_api_call():
    ...     pass
"""

import time
import logging
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
from functools import wraps
import threading

from ..exceptions import RateLimitError

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with exponential backoff.
    
    Implements rate limiting using the token bucket algorithm to control
    the rate of API calls and prevent exceeding external API limits.
    
    Attributes:
        max_calls: Maximum number of calls allowed in the period
        period: Time period in seconds
        
    Example:
        >>> limiter = RateLimiter(max_calls=100, period=60)
        >>> limiter.acquire('my_api')  # Blocks if rate limit exceeded
        >>> limiter.check_limit('my_api')  # Returns True if within limit
    """
    
    def __init__(self, max_calls: int = 100, period: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in period
            period: Time period in seconds
            
        Example:
            >>> limiter = RateLimiter(max_calls=100, period=60)  # 100 calls per minute
        """
        self.max_calls = max_calls
        self.period = period
        self._calls: Dict[str, deque] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._violations: Dict[str, int] = {}
        self._backoff_until: Dict[str, datetime] = {}
        
        logger.info(f"RateLimiter initialized: {max_calls} calls per {period} seconds")
    
    def acquire(self, key: str, wait: bool = True) -> bool:
        """
        Acquire permission to make a call.
        
        Args:
            key: Identifier for the rate-limited resource
            wait: If True, wait until rate limit allows; if False, raise error
            
        Returns:
            True if permission granted
            
        Raises:
            RateLimitError: If rate limit exceeded and wait=False
            
        Example:
            >>> limiter = RateLimiter(max_calls=10, period=60)
            >>> limiter.acquire('api_call')  # Blocks if needed
            >>> limiter.acquire('api_call', wait=False)  # Raises error if limit exceeded
        """
        # Get or create lock for this key
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        
        with self._locks[key]:
            # Check if in backoff period
            if key in self._backoff_until:
                backoff_end = self._backoff_until[key]
                if datetime.now() < backoff_end:
                    wait_time = (backoff_end - datetime.now()).total_seconds()
                    
                    if wait:
                        logger.warning(
                            f"Rate limit backoff active for {key}, waiting {wait_time:.1f}s",
                            extra={'key': key, 'wait_time': wait_time}
                        )
                        time.sleep(wait_time)
                        del self._backoff_until[key]
                    else:
                        raise RateLimitError(
                            f"Rate limit backoff active for {key}",
                            details={
                                'key': key,
                                'wait_time': wait_time,
                                'backoff_until': backoff_end.isoformat()
                            }
                        )
            
            # Initialize call history for this key
            if key not in self._calls:
                self._calls[key] = deque()
            
            current_time = time.time()
            calls = self._calls[key]
            
            # Remove old calls outside the time window
            while calls and calls[0] < current_time - self.period:
                calls.popleft()
            
            # Check if we're at the limit
            if len(calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = calls[0]
                wait_time = self.period - (current_time - oldest_call)
                
                # Record violation
                self._violations[key] = self._violations.get(key, 0) + 1
                
                # Apply exponential backoff if multiple violations
                if self._violations[key] > 3:
                    backoff_time = min(2 ** (self._violations[key] - 3), 300)  # Max 5 minutes
                    self._backoff_until[key] = datetime.now() + timedelta(seconds=backoff_time)
                    wait_time += backoff_time
                    
                    logger.warning(
                        f"Multiple rate limit violations for {key}, applying exponential backoff",
                        extra={
                            'key': key,
                            'violations': self._violations[key],
                            'backoff_seconds': backoff_time
                        }
                    )
                
                if wait:
                    logger.info(
                        f"Rate limit reached for {key}, waiting {wait_time:.1f}s",
                        extra={'key': key, 'wait_time': wait_time}
                    )
                    time.sleep(wait_time)
                    
                    # Remove the oldest call and add new one
                    calls.popleft()
                    calls.append(current_time + wait_time)
                    return True
                else:
                    raise RateLimitError(
                        f"Rate limit exceeded for {key}",
                        details={
                            'key': key,
                            'max_calls': self.max_calls,
                            'period': self.period,
                            'wait_time': wait_time,
                            'current_calls': len(calls)
                        }
                    )
            
            # Add this call to history
            calls.append(current_time)
            
            # Reset violations on successful call
            if key in self._violations and self._violations[key] > 0:
                self._violations[key] = max(0, self._violations[key] - 1)
            
            return True
    
    def check_limit(self, key: str) -> bool:
        """
        Check if rate limit allows a call without acquiring.
        
        Args:
            key: Identifier for the rate-limited resource
            
        Returns:
            True if within rate limit
            
        Example:
            >>> limiter = RateLimiter(max_calls=10, period=60)
            >>> if limiter.check_limit('api_call'):
            ...     make_api_call()
        """
        if key not in self._calls:
            return True
        
        current_time = time.time()
        calls = self._calls[key]
        
        # Count calls within the time window
        recent_calls = sum(1 for call_time in calls if call_time > current_time - self.period)
        
        return recent_calls < self.max_calls
    
    def get_remaining_calls(self, key: str) -> int:
        """
        Get number of remaining calls allowed in current period.
        
        Args:
            key: Identifier for the rate-limited resource
            
        Returns:
            Number of remaining calls
            
        Example:
            >>> limiter = RateLimiter(max_calls=10, period=60)
            >>> remaining = limiter.get_remaining_calls('api_call')
            >>> print(f"{remaining} calls remaining")
        """
        if key not in self._calls:
            return self.max_calls
        
        current_time = time.time()
        calls = self._calls[key]
        
        # Count calls within the time window
        recent_calls = sum(1 for call_time in calls if call_time > current_time - self.period)
        
        return max(0, self.max_calls - recent_calls)
    
    def get_reset_time(self, key: str) -> Optional[datetime]:
        """
        Get time when rate limit will reset.
        
        Args:
            key: Identifier for the rate-limited resource
            
        Returns:
            DateTime when limit resets, or None if not at limit
            
        Example:
            >>> limiter = RateLimiter(max_calls=10, period=60)
            >>> reset_time = limiter.get_reset_time('api_call')
            >>> if reset_time:
            ...     print(f"Limit resets at {reset_time}")
        """
        if key not in self._calls or not self._calls[key]:
            return None
        
        oldest_call = self._calls[key][0]
        reset_time = datetime.fromtimestamp(oldest_call + self.period)
        
        return reset_time
    
    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset rate limit counters.
        
        Args:
            key: Specific key to reset, or None to reset all
            
        Example:
            >>> limiter = RateLimiter(max_calls=10, period=60)
            >>> limiter.reset('api_call')  # Reset specific key
            >>> limiter.reset()  # Reset all keys
        """
        if key:
            if key in self._calls:
                self._calls[key].clear()
            if key in self._violations:
                del self._violations[key]
            if key in self._backoff_until:
                del self._backoff_until[key]
            logger.info(f"Rate limit reset for {key}")
        else:
            self._calls.clear()
            self._violations.clear()
            self._backoff_until.clear()
            logger.info("All rate limits reset")
    
    def get_statistics(self, key: str) -> Dict:
        """
        Get statistics for a rate-limited resource.
        
        Args:
            key: Identifier for the rate-limited resource
            
        Returns:
            Dictionary with statistics
            
        Example:
            >>> limiter = RateLimiter(max_calls=10, period=60)
            >>> stats = limiter.get_statistics('api_call')
            >>> print(f"Calls: {stats['current_calls']}/{stats['max_calls']}")
        """
        current_time = time.time()
        calls = self._calls.get(key, deque())
        
        recent_calls = sum(1 for call_time in calls if call_time > current_time - self.period)
        
        return {
            'key': key,
            'max_calls': self.max_calls,
            'period': self.period,
            'current_calls': recent_calls,
            'remaining_calls': max(0, self.max_calls - recent_calls),
            'violations': self._violations.get(key, 0),
            'in_backoff': key in self._backoff_until,
            'reset_time': self.get_reset_time(key),
        }


def rate_limit(max_calls: int = 100, period: int = 60, key_func: Optional[Callable] = None):
    """
    Decorator for rate limiting function calls.
    
    Args:
        max_calls: Maximum number of calls allowed in period
        period: Time period in seconds
        key_func: Optional function to generate rate limit key from function args
        
    Returns:
        Decorated function with rate limiting
        
    Example:
        >>> @rate_limit(max_calls=10, period=60)
        ... def fetch_data(symbol):
        ...     return api.get(symbol)
        
        >>> @rate_limit(max_calls=5, period=30, key_func=lambda symbol: f"api_{symbol}")
        ... def fetch_ticker(symbol):
        ...     return api.get_ticker(symbol)
    """
    limiter = RateLimiter(max_calls=max_calls, period=period)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = func.__name__
            
            # Acquire rate limit permission
            limiter.acquire(key, wait=True)
            
            # Call the function
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in rate-limited function {func.__name__}",
                    extra={'function': func.__name__, 'error': str(e)}
                )
                raise
        
        # Attach limiter to wrapper for inspection
        wrapper._rate_limiter = limiter
        
        return wrapper
    
    return decorator


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts limits based on API responses.
    
    Automatically reduces rate when receiving 429 (Too Many Requests) responses
    and gradually increases rate when successful.
    
    Example:
        >>> limiter = AdaptiveRateLimiter(max_calls=100, period=60)
        >>> limiter.acquire('api_call')
        >>> limiter.report_response('api_call', status_code=200)  # Success
        >>> limiter.report_response('api_call', status_code=429)  # Rate limited
    """
    
    def __init__(self, max_calls: int = 100, period: int = 60, min_calls: int = 10):
        """
        Initialize adaptive rate limiter.
        
        Args:
            max_calls: Initial maximum calls
            period: Time period in seconds
            min_calls: Minimum calls to maintain
        """
        super().__init__(max_calls, period)
        self.initial_max_calls = max_calls
        self.min_calls = min_calls
        self._current_max: Dict[str, int] = {}
        
        logger.info(f"AdaptiveRateLimiter initialized: {max_calls}-{min_calls} calls per {period}s")
    
    def report_response(self, key: str, status_code: int) -> None:
        """
        Report API response to adjust rate limits.
        
        Args:
            key: Identifier for the rate-limited resource
            status_code: HTTP status code from API response
            
        Example:
            >>> limiter = AdaptiveRateLimiter(max_calls=100, period=60)
            >>> response = make_api_call()
            >>> limiter.report_response('api_call', response.status_code)
        """
        if key not in self._current_max:
            self._current_max[key] = self.max_calls
        
        current_max = self._current_max[key]
        
        if status_code == 429:  # Too Many Requests
            # Reduce rate by 50%
            new_max = max(self.min_calls, int(current_max * 0.5))
            self._current_max[key] = new_max
            
            logger.warning(
                f"Rate limit hit for {key}, reducing to {new_max} calls per {self.period}s",
                extra={'key': key, 'old_max': current_max, 'new_max': new_max}
            )
            
            # Apply immediate backoff
            self._backoff_until[key] = datetime.now() + timedelta(seconds=self.period)
            
        elif 200 <= status_code < 300:  # Success
            # Gradually increase rate by 10%
            if current_max < self.initial_max_calls:
                new_max = min(self.initial_max_calls, int(current_max * 1.1))
                self._current_max[key] = new_max
                
                logger.debug(
                    f"Increasing rate limit for {key} to {new_max} calls per {self.period}s",
                    extra={'key': key, 'old_max': current_max, 'new_max': new_max}
                )
    
    def get_current_max(self, key: str) -> int:
        """
        Get current maximum calls for key.
        
        Args:
            key: Identifier for the rate-limited resource
            
        Returns:
            Current maximum calls allowed
        """
        return self._current_max.get(key, self.max_calls)


# Global rate limiters for common use cases
_api_rate_limiter: Optional[RateLimiter] = None
_data_fetch_limiter: Optional[RateLimiter] = None


def get_api_rate_limiter() -> RateLimiter:
    """
    Get global API rate limiter.
    
    Returns:
        Global RateLimiter for API calls
        
    Example:
        >>> from cryptvault.security import get_api_rate_limiter
        >>> limiter = get_api_rate_limiter()
        >>> limiter.acquire('yfinance')
    """
    global _api_rate_limiter
    if _api_rate_limiter is None:
        _api_rate_limiter = RateLimiter(max_calls=100, period=60)
    return _api_rate_limiter


def get_data_fetch_limiter() -> RateLimiter:
    """
    Get global data fetch rate limiter.
    
    Returns:
        Global RateLimiter for data fetching
        
    Example:
        >>> from cryptvault.security import get_data_fetch_limiter
        >>> limiter = get_data_fetch_limiter()
        >>> limiter.acquire('fetch_btc')
    """
    global _data_fetch_limiter
    if _data_fetch_limiter is None:
        _data_fetch_limiter = AdaptiveRateLimiter(max_calls=50, period=60, min_calls=10)
    return _data_fetch_limiter
