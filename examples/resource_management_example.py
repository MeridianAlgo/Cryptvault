"""
Resource Management Example

This script demonstrates how to use CryptVault's resource management
utilities for efficient resource handling.

Usage:
    python examples/resource_management_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cryptvault.utils.resource_manager import (
    managed_connection,
    managed_memory,
    managed_file,
    get_connection_pool,
    get_resource_monitor,
    optimize_memory,
    limit_memory_usage
)
from cryptvault.core.analyzer import PatternAnalyzer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_connection_pooling():
    """Demonstrate connection pooling for HTTP requests."""
    print("\n" + "=" * 80)
    print("Example 1: Connection Pooling")
    print("=" * 80)

    pool = get_connection_pool()

    # Multiple requests reuse connections
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1'
    ]

    for i, url in enumerate(urls, 1):
        try:
            with managed_connection(url) as response:
                print(f"Request {i}: Status {response.status_code}")
        except Exception as e:
            print(f"Request {i} failed: {e}")

    # Show pool statistics
    stats = pool.get_stats()
    print(f"\nConnection Pool Stats:")
    print(f"  Total Requests: {stats['request_count']}")
    print(f"  Errors: {stats['error_count']}")
    print(f"  Error Rate: {stats['error_rate']:.2%}")


def example_memory_management():
    """Demonstrate memory profiling and management."""
    print("\n" + "=" * 80)
    print("Example 2: Memory Management")
    print("=" * 80)

    # Track memory usage
    with managed_memory("data_processing", threshold_mb=100) as stats:
        # Simulate memory-intensive operation
        large_list = [i for i in range(1000000)]
        processed = [x * 2 for x in large_list]

    print(f"\nMemory Stats:")
    print(f"  Start: {stats.memory_start_mb:.2f} MB")
    print(f"  End: {stats.memory_end_mb:.2f} MB")
    print(f"  Peak: {stats.memory_peak_mb:.2f} MB")
    print(f"  Delta: {stats.get_memory_delta():+.2f} MB")
    print(f"  Duration: {stats.duration_seconds:.4f}s")

    # Optimize memory
    print("\nOptimizing memory...")
    optimize_memory()


def example_resource_monitoring():
    """Demonstrate resource monitoring across operations."""
    print("\n" + "=" * 80)
    print("Example 3: Resource Monitoring")
    print("=" * 80)

    monitor = get_resource_monitor()
    monitor.clear()

    # Track multiple operations
    operations = ['operation_1', 'operation_2', 'operation_3']

    for op_name in operations:
        with monitor.track_operation(op_name):
            # Simulate work
            data = [i ** 2 for i in range(100000)]

    # Get summary
    summary = monitor.get_summary()

    print("\nResource Usage Summary:")
    for op_name, stats in summary.items():
        print(f"\n{op_name}:")
        print(f"  Count: {stats['count']}")
        print(f"  Avg Memory: {stats['avg_memory_mb']:.2f} MB")
        print(f"  Max Memory: {stats['max_memory_mb']:.2f} MB")
        print(f"  Avg Duration: {stats['avg_duration_seconds']:.4f}s")


@limit_memory_usage(max_mb=200)
def example_memory_limited_function():
    """Demonstrate memory-limited function execution."""
    print("\n" + "=" * 80)
    print("Example 4: Memory-Limited Function")
    print("=" * 80)

    # This function has a memory limit
    data = [i for i in range(500000)]
    result = sum(data)

    print(f"Processed {len(data)} items")
    print(f"Result: {result}")

    return result


def example_file_management():
    """Demonstrate file resource management."""
    print("\n" + "=" * 80)
    print("Example 5: File Resource Management")
    print("=" * 80)

    # Create a temporary file
    temp_file = "temp_example.txt"

    # Write with managed file
    with managed_file(temp_file, 'w') as f:
        f.write("This is a test file\n")
        f.write("Resources are automatically cleaned up\n")
        print(f"File written: {temp_file}")

    # Read with managed file
    with managed_file(temp_file, 'r') as f:
        content = f.read()
        print(f"File content:\n{content}")

    # Cleanup
    import os
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"Temporary file removed")


def example_analysis_with_monitoring():
    """Demonstrate analysis with resource monitoring."""
    print("\n" + "=" * 80)
    print("Example 6: Analysis with Resource Monitoring")
    print("=" * 80)

    monitor = get_resource_monitor()

    try:
        with monitor.track_operation("full_analysis") as stats:
            analyzer = PatternAnalyzer()
            result = analyzer.analyze_ticker('BTC', days=30)

        print(f"\nAnalysis completed:")
        print(f"  Success: {result.success}")
        print(f"  Patterns Found: {len(result.patterns)}")
        print(f"  Analysis Time: {result.analysis_time:.2f}s")
        print(f"\nResource Usage:")
        print(f"  Peak Memory: {stats.memory_peak_mb:.2f} MB")
        print(f"  Duration: {stats.duration_seconds:.2f}s")

    except Exception as e:
        print(f"Analysis failed: {e}")


def main():
    """Run all examples."""
    print("=" * 80)
    print("CryptVault Resource Management Examples")
    print("=" * 80)

    try:
        # Run examples
        example_connection_pooling()
        example_memory_management()
        example_resource_monitoring()
        example_memory_limited_function()
        example_file_management()
        example_analysis_with_monitoring()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nError running examples: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Examples completed")
    print("=" * 80)


if __name__ == '__main__':
    main()
