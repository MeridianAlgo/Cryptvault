"""
Performance Benchmarking Script

This script profiles and benchmarks the CryptVault analysis workflow to identify
performance bottlenecks and measure execution times of critical operations.

Usage:
    python scripts/benchmark_performance.py [--symbol BTC] [--days 60] [--iterations 10]

Output:
    - Detailed performance report
    - Bottleneck identification
    - Recommendations for optimization
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cryptvault.core.analyzer import PatternAnalyzer
from cryptvault.utils.profiling import (
    get_profiler,
    benchmark_operation,
    profile_memory,
    generate_performance_report,
    benchmark_function
)
from cryptvault.indicators.trend import calculate_sma, calculate_ema
from cryptvault.indicators.momentum import calculate_rsi, calculate_macd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def benchmark_analysis_workflow(symbol: str = "BTC", days: int = 60, iterations: int = 5):
    """
    Benchmark the complete analysis workflow.

    Args:
        symbol: Ticker symbol to analyze
        days: Number of days of data
        iterations: Number of iterations to run

    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking analysis workflow for {symbol} ({iterations} iterations)")

    analyzer = PatternAnalyzer()
    profiler = get_profiler()
    profiler.clear()

    results = {
        'symbol': symbol,
        'days': days,
        'iterations': iterations,
        'iteration_times': [],
        'component_times': {},
        'memory_usage': {}
    }

    for i in range(iterations):
        logger.info(f"Iteration {i+1}/{iterations}")

        with benchmark_operation(f"full_analysis_iter_{i+1}"):
            with profile_memory(f"analysis_memory_iter_{i+1}") as mem_stats:
                result = analyzer.analyze_ticker(symbol, days=days)

        results['iteration_times'].append(result.analysis_time)
        results['memory_usage'][f'iter_{i+1}'] = mem_stats['peak_mb']

        if not result.success:
            logger.warning(f"Analysis failed: {result.errors}")

    # Calculate statistics
    times = results['iteration_times']
    results['avg_time'] = sum(times) / len(times)
    results['min_time'] = min(times)
    results['max_time'] = max(times)
    results['std_dev'] = (sum((t - results['avg_time'])**2 for t in times) / len(times))**0.5

    # Get profiler summary
    results['profiler_summary'] = profiler.get_summary()

    return results


def benchmark_indicators(data_size: int = 1000):
    """
    Benchmark technical indicator calculations.

    Args:
        data_size: Number of data points to use

    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking indicators with {data_size} data points")

    # Generate sample data
    import numpy as np
    prices = np.random.uniform(40000, 50000, data_size).tolist()
    highs = [p * 1.01 for p in prices]
    lows = [p * 0.99 for p in prices]
    closes = prices

    results = {}

    # Benchmark SMA
    logger.info("Benchmarking SMA...")
    results['sma_20'] = benchmark_function(calculate_sma, 100, prices, 20)
    results['sma_50'] = benchmark_function(calculate_sma, 100, prices, 50)
    results['sma_200'] = benchmark_function(calculate_sma, 100, prices, 200)

    # Benchmark EMA
    logger.info("Benchmarking EMA...")
    results['ema_12'] = benchmark_function(calculate_ema, 100, prices, 12)
    results['ema_26'] = benchmark_function(calculate_ema, 100, prices, 26)

    # Benchmark RSI
    logger.info("Benchmarking RSI...")
    results['rsi_14'] = benchmark_function(calculate_rsi, 100, prices, 14)

    # Benchmark MACD
    logger.info("Benchmarking MACD...")
    results['macd'] = benchmark_function(calculate_macd, 100, prices)

    return results


def benchmark_pattern_detection(symbol: str = "BTC", days: int = 60):
    """
    Benchmark pattern detection components.

    Args:
        symbol: Ticker symbol
        days: Number of days of data

    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking pattern detection for {symbol}")

    analyzer = PatternAnalyzer()

    # Fetch data once
    with benchmark_operation("data_fetch"):
        result = analyzer.analyze_ticker(symbol, days=days)

    if not result.success:
        logger.error("Failed to fetch data for pattern detection benchmark")
        return {}

    profiler = get_profiler()
    summary = profiler.get_summary()

    # Extract pattern detection times
    pattern_times = {}
    for op_name, stats in summary['operations'].items():
        if 'pattern' in op_name.lower() or 'detect' in op_name.lower():
            pattern_times[op_name] = stats

    return {
        'total_patterns_found': len(result.patterns),
        'pattern_detection_times': pattern_times
    }


def identify_bottlenecks(profiler_summary: dict) -> list:
    """
    Identify performance bottlenecks from profiler data.

    Args:
        profiler_summary: Summary from profiler

    Returns:
        List of bottlenecks with recommendations
    """
    bottlenecks = []

    operations = profiler_summary.get('operations', {})

    # Sort by total time
    sorted_ops = sorted(
        operations.items(),
        key=lambda x: x[1]['total_time'],
        reverse=True
    )

    # Identify slow operations (> 1 second total or > 500ms average)
    for op_name, stats in sorted_ops[:10]:  # Top 10
        if stats['total_time'] > 1.0 or stats['avg_time'] > 0.5:
            bottleneck = {
                'operation': op_name,
                'total_time_ms': stats['total_time_ms'],
                'avg_time_ms': stats['avg_time_ms'],
                'count': stats['count'],
                'severity': 'high' if stats['avg_time'] > 1.0 else 'medium'
            }

            # Add recommendations
            if 'fetch' in op_name.lower() or 'api' in op_name.lower():
                bottleneck['recommendation'] = "Consider caching API responses or using connection pooling"
            elif 'pattern' in op_name.lower():
                bottleneck['recommendation'] = "Optimize pattern detection algorithms or reduce search space"
            elif 'indicator' in op_name.lower():
                bottleneck['recommendation'] = "Ensure NumPy vectorization is used for calculations"
            elif 'ml' in op_name.lower() or 'predict' in op_name.lower():
                bottleneck['recommendation'] = "Cache predictions or optimize model inference"
            else:
                bottleneck['recommendation'] = "Profile this operation in detail to identify specific issues"

            bottlenecks.append(bottleneck)

    return bottlenecks


def generate_benchmark_report(results: dict) -> str:
    """
    Generate formatted benchmark report.

    Args:
        results: Benchmark results dictionary

    Returns:
        Formatted report string
    """
    lines = [
        "=" * 80,
        "CRYPTVAULT PERFORMANCE BENCHMARK REPORT",
        "=" * 80,
        "",
        f"Symbol: {results.get('symbol', 'N/A')}",
        f"Data Points: {results.get('days', 'N/A')} days",
        f"Iterations: {results.get('iterations', 'N/A')}",
        "",
        "Analysis Workflow Performance:",
        "-" * 80,
        f"Average Time: {results.get('avg_time', 0):.4f}s ({results.get('avg_time', 0)*1000:.2f}ms)",
        f"Min Time: {results.get('min_time', 0):.4f}s",
        f"Max Time: {results.get('max_time', 0):.4f}s",
        f"Std Dev: {results.get('std_dev', 0):.4f}s",
        "",
    ]

    # Memory usage
    if results.get('memory_usage'):
        mem_values = list(results['memory_usage'].values())
        avg_mem = sum(mem_values) / len(mem_values)
        lines.extend([
            "Memory Usage:",
            "-" * 80,
            f"Average Peak Memory: {avg_mem:.2f} MB",
            f"Min Peak Memory: {min(mem_values):.2f} MB",
            f"Max Peak Memory: {max(mem_values):.2f} MB",
            ""
        ])

    # Performance assessment
    avg_time = results.get('avg_time', 0)
    if avg_time < 2.0:
        assessment = "EXCELLENT - Well within performance targets"
    elif avg_time < 5.0:
        assessment = "GOOD - Meets performance requirements"
    elif avg_time < 10.0:
        assessment = "ACCEPTABLE - Consider optimization"
    else:
        assessment = "NEEDS IMPROVEMENT - Optimization required"

    lines.extend([
        "Performance Assessment:",
        "-" * 80,
        f"Status: {assessment}",
        f"Target: < 5.0 seconds for 1000 data points",
        f"Current: {avg_time:.2f} seconds",
        ""
    ])

    # Bottlenecks
    if 'bottlenecks' in results:
        lines.extend([
            "Identified Bottlenecks:",
            "-" * 80
        ])

        for i, bottleneck in enumerate(results['bottlenecks'], 1):
            lines.extend([
                f"\n{i}. {bottleneck['operation']}",
                f"   Severity: {bottleneck['severity'].upper()}",
                f"   Total Time: {bottleneck['total_time_ms']:.2f}ms",
                f"   Average Time: {bottleneck['avg_time_ms']:.2f}ms",
                f"   Call Count: {bottleneck['count']}",
                f"   Recommendation: {bottleneck['recommendation']}"
            ])

    lines.append("\n" + "=" * 80)

    return "\n".join(lines)


def main():
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(description="Benchmark CryptVault performance")
    parser.add_argument('--symbol', default='BTC', help='Ticker symbol to analyze')
    parser.add_argument('--days', type=int, default=60, help='Number of days of data')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations')
    parser.add_argument('--indicators-only', action='store_true', help='Only benchmark indicators')
    parser.add_argument('--output', help='Output file for report')

    args = parser.parse_args()

    print("=" * 80)
    print("CryptVault Performance Benchmarking")
    print("=" * 80)
    print()

    if args.indicators_only:
        # Benchmark indicators only
        print("Benchmarking technical indicators...")
        indicator_results = benchmark_indicators(data_size=1000)

        print("\nIndicator Benchmark Results:")
        print("-" * 80)
        for indicator, stats in indicator_results.items():
            print(f"\n{indicator}:")
            print(f"  Average: {stats['avg_time_ms']:.2f}ms")
            print(f"  Min: {stats['min_time_ms']:.2f}ms")
            print(f"  Max: {stats['max_time_ms']:.2f}ms")
            print(f"  Std Dev: {stats['std_dev_ms']:.2f}ms")

    else:
        # Full workflow benchmark
        print(f"Benchmarking analysis workflow for {args.symbol}...")
        print(f"Iterations: {args.iterations}")
        print()

        results = benchmark_analysis_workflow(
            symbol=args.symbol,
            days=args.days,
            iterations=args.iterations
        )

        # Identify bottlenecks
        if 'profiler_summary' in results:
            results['bottlenecks'] = identify_bottlenecks(results['profiler_summary'])

        # Generate report
        report = generate_benchmark_report(results)
        print(report)

        # Generate detailed profiler report
        print("\n")
        print(generate_performance_report())

        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
                f.write("\n\n")
                f.write(generate_performance_report())
            print(f"\nReport saved to: {args.output}")


if __name__ == '__main__':
    main()
