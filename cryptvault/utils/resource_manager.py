"""
Resource Management Utilities

This module provides utilities for managing system resources including:
- Context managers for automatic resource cleanup
- Connection pooling for HTTP requests
- Memory profiling and optimization
- File handle management

These utilities ensure resources are properly released and prevent resource leaks.

Example:
    >>> from cryptvault.utils.resource_manager import managed_connection
    >>> with managed_connection(url) as conn:
    ...     data = conn.get()
"""

import logging
import time
import tracemalloc
from contextlib import contextmanager
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import gc

logger = logging.getLogger(__name__)


@dataclass
class ResourceStats:
    """
    Statistics for resource usage.

    Attributes:
        memory_start_mb: Memory at start in MB
        memory_end_mb: Memory at end in MB
        memory_peak_mb: Peak memory usage in MB
        duration_seconds: Duration in seconds
        resource_type: Type of resource
    """
    memory_start_mb: float
    memory_end_mb: float
    memory_peak_mb: float
    duration_seconds: float
    resource_type: str

    def get_memory_delta(self) -> float:
        """Get memory change in MB."""
        return self.memory_end_mb - self.memory_start_mb


class ConnectionPool:
    """
    HTTP connection pool with retry logic and timeout management.

    This class provides a reusable connection pool for HTTP requests
    with automatic retry, timeout handling, and connection limits.

    Example:
        >>> pool = ConnectionPool(max_connections=10)
        >>> response = pool.get('https://api.example.com/data')
    """

    def __init__(
        self,
        max_connections: int = 10,
        max_retries: int = 3,
        timeout: int = 30,
        backoff_factor: float = 0.3
    ):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum number of connections
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            backoff_factor: Backoff factor for retries
        """
        self.max_connections = max_connections
        self.timeout = timeout

        # Create session with retry strategy
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=max_connections,
            pool_maxsize=max_connections
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self._request_count = 0
        self._error_count = 0

        logger.info(f"Connection pool initialized with {max_connections} max connections")

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Perform GET request with connection pooling.

        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        kwargs.setdefault('timeout', self.timeout)

        try:
            self._request_count += 1
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self._error_count += 1
            logger.error(f"Request failed: {url} - {e}")
            raise

    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Perform POST request with connection pooling.

        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.post

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        kwargs.setdefault('timeout', self.timeout)

        try:
            self._request_count += 1
            response = self.session.post(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self._error_count += 1
            logger.error(f"POST request failed: {url} - {e}")
            raise

    def close(self) -> None:
        """Close all connections in the pool."""
        self.session.close()
        logger.info("Connection pool closed")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        return {
            'max_connections': self.max_connections,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(1, self._request_count)
        }


# Global connection pool
_global_pool: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """
    Get or create the global connection pool.

    Returns:
        Global ConnectionPool instance
    """
    global _global_pool
    if _global_pool is None:
        _global_pool = ConnectionPool()
    return _global_pool


@contextmanager
def managed_connection(url: str, **kwargs):
    """
    Context manager for managed HTTP connections.

    This context manager ensures connections are properly handled
    and resources are released even if errors occur.

    Args:
        url: URL to connect to
        **kwargs: Additional arguments for request

    Yields:
        Response object

    Example:
        >>> with managed_connection('https://api.example.com') as response:
        ...     data = response.json()
    """
    pool = get_connection_pool()
    response = None

    try:
        response = pool.get(url, **kwargs)
        yield response
    finally:
        if response is not None:
            response.close()


@contextmanager
def managed_memory(operation_name: str, threshold_mb: float = 100.0):
    """
    Context manager for memory profiling and management.

    This context manager tracks memory usage and can trigger garbage
    collection if memory usage exceeds threshold.

    Args:
        operation_name: Name of the operation
        threshold_mb: Memory threshold in MB for GC trigger

    Yields:
        ResourceStats object (populated after block execution)

    Example:
        >>> with managed_memory("data_processing", threshold_mb=500) as stats:
        ...     process_large_dataset(data)
        >>> print(f"Memory used: {stats.memory_peak_mb:.2f} MB")
    """
    # Start memory tracking
    tracemalloc.start()
    start_time = time.time()

    current, _ = tracemalloc.get_traced_memory()
    memory_start_mb = current / 1024 / 1024

    stats = ResourceStats(
        memory_start_mb=memory_start_mb,
        memory_end_mb=0.0,
        memory_peak_mb=0.0,
        duration_seconds=0.0,
        resource_type="memory"
    )

    try:
        yield stats
    finally:
        # Get final memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        stats.memory_end_mb = current / 1024 / 1024
        stats.memory_peak_mb = peak / 1024 / 1024
        stats.duration_seconds = time.time() - start_time

        memory_delta = stats.get_memory_delta()

        logger.debug(
            f"Memory stats for '{operation_name}': "
            f"Start={stats.memory_start_mb:.2f}MB, "
            f"End={stats.memory_end_mb:.2f}MB, "
            f"Peak={stats.memory_peak_mb:.2f}MB, "
            f"Delta={memory_delta:+.2f}MB"
        )

        # Trigger GC if memory usage is high
        if stats.memory_peak_mb > threshold_mb:
            logger.warning(
                f"High memory usage detected ({stats.memory_peak_mb:.2f}MB), "
                "triggering garbage collection"
            )
            gc.collect()


@contextmanager
def managed_file(filepath: str, mode: str = 'r', **kwargs):
    """
    Context manager for file operations with automatic cleanup.

    Args:
        filepath: Path to file
        mode: File open mode
        **kwargs: Additional arguments for open()

    Yields:
        File object

    Example:
        >>> with managed_file('data.csv', 'r') as f:
        ...     data = f.read()
    """
    file_obj = None

    try:
        file_obj = open(filepath, mode, **kwargs)
        yield file_obj
    finally:
        if file_obj is not None:
            file_obj.close()
            logger.debug(f"File closed: {filepath}")


class ResourceMonitor:
    """
    Monitor and track resource usage across operations.

    This class provides centralized monitoring of resource usage
    including memory, connections, and file handles.

    Example:
        >>> monitor = ResourceMonitor()
        >>> with monitor.track_operation("analysis"):
        ...     perform_analysis()
        >>> print(monitor.get_summary())
    """

    def __init__(self):
        """Initialize resource monitor."""
        self.operations: Dict[str, list] = {}
        self._active_operations: Dict[str, float] = {}

    @contextmanager
    def track_operation(self, operation_name: str):
        """
        Track resource usage for an operation.

        Args:
            operation_name: Name of the operation

        Yields:
            ResourceStats object
        """
        with managed_memory(operation_name) as stats:
            yield stats

        # Record stats
        if operation_name not in self.operations:
            self.operations[operation_name] = []
        self.operations[operation_name].append(stats)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all tracked operations.

        Returns:
            Dictionary with operation summaries
        """
        summary = {}

        for op_name, stats_list in self.operations.items():
            if not stats_list:
                continue

            avg_memory = sum(s.memory_peak_mb for s in stats_list) / len(stats_list)
            max_memory = max(s.memory_peak_mb for s in stats_list)
            avg_duration = sum(s.duration_seconds for s in stats_list) / len(stats_list)

            summary[op_name] = {
                'count': len(stats_list),
                'avg_memory_mb': round(avg_memory, 2),
                'max_memory_mb': round(max_memory, 2),
                'avg_duration_seconds': round(avg_duration, 4)
            }

        return summary

    def clear(self) -> None:
        """Clear all tracked operations."""
        self.operations.clear()
        self._active_operations.clear()


# Global resource monitor
_global_monitor = ResourceMonitor()


def get_resource_monitor() -> ResourceMonitor:
    """Get the global resource monitor."""
    return _global_monitor


def optimize_memory():
    """
    Optimize memory usage by triggering garbage collection.

    This function should be called after large operations to
    ensure memory is released promptly.
    """
    logger.debug("Optimizing memory usage...")

    # Get memory before GC
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()

    # Run garbage collection
    collected = gc.collect()

    # Get memory after GC
    after, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    freed_mb = (before - after) / 1024 / 1024

    logger.info(
        f"Memory optimization complete: "
        f"Collected {collected} objects, "
        f"Freed {freed_mb:.2f}MB"
    )


def limit_memory_usage(max_mb: float = 1000.0) -> Callable:
    """
    Decorator to limit memory usage of a function.

    If memory usage exceeds the limit, garbage collection is triggered.

    Args:
        max_mb: Maximum memory usage in MB

    Returns:
        Decorated function

    Example:
        >>> @limit_memory_usage(max_mb=500)
        ... def process_data(data):
        ...     # processing code
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with managed_memory(func.__name__, threshold_mb=max_mb) as stats:
                result = func(*args, **kwargs)

            if stats.memory_peak_mb > max_mb:
                logger.warning(
                    f"Function '{func.__name__}' exceeded memory limit: "
                    f"{stats.memory_peak_mb:.2f}MB > {max_mb}MB"
                )

            return result

        return wrapper

    return decorator


@contextmanager
def resource_cleanup(*cleanup_funcs):
    """
    Context manager for ensuring cleanup functions are called.

    Args:
        *cleanup_funcs: Functions to call on cleanup

    Yields:
        None

    Example:
        >>> def cleanup():
        ...     close_connections()
        >>> with resource_cleanup(cleanup):
        ...     perform_operations()
    """
    try:
        yield
    finally:
        for cleanup_func in cleanup_funcs:
            try:
                cleanup_func()
            except Exception as e:
                logger.error(f"Cleanup function failed: {e}")


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.

    Returns:
        Dictionary with memory statistics in MB
    """
    tracemalloc.start()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'current_mb': current / 1024 / 1024,
        'peak_mb': peak / 1024 / 1024
    }
