"""
Performance Profiling and Benchmarking Utilities

This module provides tools for profiling code performance, identifying bottlenecks,
and benchmarking critical operations. It includes decorators, context managers,
and reporting utilities for comprehensive performance analysis.

Time Complexity: O(1) overhead per measurement
Memory Overhead: Minimal (~100 bytes per measurement)

Example:
    >>> from cryptvault.utils.profiling import profile_function, benchmark_operation
    >>> @profile_function
    ... def my_function():
    ...     # function code
    >>> with benchmark_operation("data_fetch"):
    ...     # operation code
"""

import time
import functools
import logging
import cProfile
import pstats
import io
from typing import Callable, Dict, Any, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import tracemalloc

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """
    Container for performance metrics.

    Attributes:
        operation_name: Name of the operation
        execution_time: Time taken in seconds
        memory_used: Memory used in MB (if tracked)
        call_count: Number of times called
        timestamp: When measurement was taken
        metadata: Additional metadata
    """
    operation_name: str
    execution_time: float
    memory_used: Optional[float] = None
    call_count: int = 1
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'operation': self.operation_name,
            'execution_time_seconds': round(self.execution_time, 4),
            'execution_time_ms': round(self.execution_time * 1000, 2),
            'memory_mb': round(self.memory_used, 2) if self.memory_used else None,
            'call_count': self.call_count,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class PerformanceProfiler:
    """
    Performance profiler for tracking and analyzing execution metrics.

    This class provides centralized performance tracking with support for:
    - Function-level profiling
    - Operation benchmarking
    - Memory profiling
    - Statistical analysis
    - Report generation

    Example:
        >>> profiler = PerformanceProfiler()
        >>> profiler.start_operation("data_fetch")
        >>> # ... operation code ...
        >>> profiler.end_operation("data_fetch")
        >>> print(profiler.get_summary())
    """

    def __init__(self):
        """Initialize performance profiler."""
        self.metrics: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, float] = {}
        self.memory_tracking_enabled = False

    def start_operation(self, operation_name: str, metadata: Optional[Dict] = None) -> None:
        """
        Start tracking an operation.

        Args:
            operation_name: Name of the operation
            metadata: Optional metadata to attach
        """
        self.active_operations[operation_name] = time.perf_counter()
        if metadata:
            self.active_operations[f"{operation_name}_metadata"] = metadata

    def end_operation(self, operation_name: str) -> PerformanceMetrics:
        """
        End tracking an operation and record metrics.

        Args:
            operation_name: Name of the operation

        Returns:
            PerformanceMetrics for the operation

        Raises:
            ValueError: If operation was not started
        """
        if operation_name not in self.active_operations:
            raise ValueError(f"Operation '{operation_name}' was not started")

        start_time = self.active_operations.pop(operation_name)
        execution_time = time.perf_counter() - start_time

        metadata = self.active_operations.pop(f"{operation_name}_metadata", {})

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            metadata=metadata
        )

        self.metrics.append(metrics)
        logger.debug(f"Operation '{operation_name}' completed in {execution_time:.4f}s")

        return metrics

    def record_metric(self, metrics: PerformanceMetrics) -> None:
        """
        Record a performance metric.

        Args:
            metrics: PerformanceMetrics to record
        """
        self.metrics.append(metrics)

    def get_metrics_by_operation(self, operation_name: str) -> List[PerformanceMetrics]:
        """
        Get all metrics for a specific operation.

        Args:
            operation_name: Name of the operation

        Returns:
            List of metrics for the operation
        """
        return [m for m in self.metrics if m.operation_name == operation_name]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all recorded metrics.

        Returns:
            Dictionary with summary statistics including:
            - total_operations: Total number of operations tracked
            - total_time: Total execution time
            - operations: Per-operation statistics
        """
        if not self.metrics:
            return {
                'total_operations': 0,
                'total_time_seconds': 0.0,
                'operations': {}
            }

        # Group by operation
        operations_summary = {}
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in operations_summary:
                operations_summary[op_name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'times': []
                }

            op_stats = operations_summary[op_name]
            op_stats['count'] += 1
            op_stats['total_time'] += metric.execution_time
            op_stats['min_time'] = min(op_stats['min_time'], metric.execution_time)
            op_stats['max_time'] = max(op_stats['max_time'], metric.execution_time)
            op_stats['times'].append(metric.execution_time)

        # Calculate averages and format
        for op_name, stats in operations_summary.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['total_time_ms'] = round(stats['total_time'] * 1000, 2)
            stats['avg_time_ms'] = round(stats['avg_time'] * 1000, 2)
            stats['min_time_ms'] = round(stats['min_time'] * 1000, 2)
            stats['max_time_ms'] = round(stats['max_time'] * 1000, 2)
            del stats['times']  # Remove raw times from summary

        total_time = sum(m.execution_time for m in self.metrics)

        return {
            'total_operations': len(self.metrics),
            'total_time_seconds': round(total_time, 4),
            'total_time_ms': round(total_time * 1000, 2),
            'operations': operations_summary
        }

    def clear(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()
        self.active_operations.clear()


# Global profiler instance
_global_profiler = PerformanceProfiler()


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance."""
    return _global_profiler


def profile_function(func: Callable) -> Callable:
    """
    Decorator to profile function execution time.

    This decorator measures and logs the execution time of the decorated function.
    Metrics are recorded in the global profiler.

    Args:
        func: Function to profile

    Returns:
        Wrapped function with profiling

    Example:
        >>> @profile_function
        ... def calculate_indicators(data):
        ...     # calculation code
        ...     pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        operation_name = f"{func.__module__}.{func.__name__}"
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.perf_counter() - start_time
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                execution_time=execution_time
            )
            _global_profiler.record_metric(metrics)

            if execution_time > 1.0:  # Log slow operations
                logger.warning(f"Slow operation: {operation_name} took {execution_time:.2f}s")

    return wrapper


@contextmanager
def benchmark_operation(operation_name: str, metadata: Optional[Dict] = None):
    """
    Context manager for benchmarking operations.

    This context manager measures the execution time of a code block
    and records it in the global profiler.

    Args:
        operation_name: Name of the operation
        metadata: Optional metadata to attach

    Yields:
        PerformanceMetrics object (populated after block execution)

    Example:
        >>> with benchmark_operation("data_fetch", {"symbol": "BTC"}):
        ...     data = fetch_data("BTC")
    """
    metrics = PerformanceMetrics(
        operation_name=operation_name,
        execution_time=0.0,
        metadata=metadata or {}
    )

    start_time = time.perf_counter()

    try:
        yield metrics
    finally:
        metrics.execution_time = time.perf_counter() - start_time
        _global_profiler.record_metric(metrics)


@contextmanager
def profile_memory(operation_name: str):
    """
    Context manager for profiling memory usage.

    This context manager tracks memory allocation during a code block
    using tracemalloc.

    Args:
        operation_name: Name of the operation

    Yields:
        Dictionary with memory statistics (populated after block execution)

    Example:
        >>> with profile_memory("pattern_detection") as mem_stats:
        ...     patterns = detect_patterns(data)
        >>> print(f"Memory used: {mem_stats['peak_mb']:.2f} MB")
    """
    mem_stats = {'peak_mb': 0.0, 'current_mb': 0.0}

    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        yield mem_stats
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        execution_time = time.perf_counter() - start_time

        mem_stats['current_mb'] = current / 1024 / 1024
        mem_stats['peak_mb'] = peak / 1024 / 1024

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            memory_used=mem_stats['peak_mb']
        )
        _global_profiler.record_metric(metrics)

        logger.debug(
            f"Memory profile for '{operation_name}': "
            f"Peak={mem_stats['peak_mb']:.2f}MB, Time={execution_time:.4f}s"
        )


def profile_with_cprofile(func: Callable) -> Callable:
    """
    Decorator to profile function with cProfile.

    This decorator provides detailed profiling information including
    function call counts and time spent in each function.

    Args:
        func: Function to profile

    Returns:
        Wrapped function with cProfile profiling

    Example:
        >>> @profile_with_cprofile
        ... def complex_analysis(data):
        ...     # analysis code
        ...     pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()

            # Print stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 functions

            logger.info(f"cProfile results for {func.__name__}:\n{s.getvalue()}")

    return wrapper


def benchmark_function(func: Callable, iterations: int = 100, *args, **kwargs) -> Dict[str, Any]:
    """
    Benchmark a function over multiple iterations.

    Args:
        func: Function to benchmark
        iterations: Number of iterations to run
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function

    Returns:
        Dictionary with benchmark results:
        - iterations: Number of iterations
        - total_time: Total execution time
        - avg_time: Average time per iteration
        - min_time: Minimum time
        - max_time: Maximum time

    Example:
        >>> results = benchmark_function(calculate_rsi, 100, prices, period=14)
        >>> print(f"Average time: {results['avg_time_ms']:.2f}ms")
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        times.append(time.perf_counter() - start)

    return {
        'iterations': iterations,
        'total_time_seconds': sum(times),
        'avg_time_seconds': sum(times) / iterations,
        'avg_time_ms': (sum(times) / iterations) * 1000,
        'min_time_seconds': min(times),
        'min_time_ms': min(times) * 1000,
        'max_time_seconds': max(times),
        'max_time_ms': max(times) * 1000,
        'std_dev_ms': (sum((t - sum(times)/iterations)**2 for t in times) / iterations)**0.5 * 1000
    }


def generate_performance_report() -> str:
    """
    Generate a formatted performance report.

    Returns:
        Formatted string with performance statistics

    Example:
        >>> report = generate_performance_report()
        >>> print(report)
    """
    summary = _global_profiler.get_summary()

    if summary['total_operations'] == 0:
        return "No performance data collected."

    lines = [
        "=" * 80,
        "PERFORMANCE REPORT",
        "=" * 80,
        f"Total Operations: {summary['total_operations']}",
        f"Total Time: {summary['total_time_ms']:.2f}ms ({summary['total_time_seconds']:.4f}s)",
        "",
        "Operation Breakdown:",
        "-" * 80
    ]

    # Sort operations by total time
    operations = sorted(
        summary['operations'].items(),
        key=lambda x: x[1]['total_time'],
        reverse=True
    )

    for op_name, stats in operations:
        lines.append(f"\n{op_name}:")
        lines.append(f"  Count: {stats['count']}")
        lines.append(f"  Total: {stats['total_time_ms']:.2f}ms")
        lines.append(f"  Average: {stats['avg_time_ms']:.2f}ms")
        lines.append(f"  Min: {stats['min_time_ms']:.2f}ms")
        lines.append(f"  Max: {stats['max_time_ms']:.2f}ms")

    lines.append("\n" + "=" * 80)

    return "\n".join(lines)
