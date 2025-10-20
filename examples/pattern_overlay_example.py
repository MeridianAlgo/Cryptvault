"""
Example: Using Pattern Overlay on Custom Charts

This example demonstrates how to use the PatternOverlay class
to draw detected patterns on your own matplotlib charts.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

# Import CryptVault components
from cryptvault.analyzer import PatternAnalyzer
from cryptvault.data.package_fetcher import PackageDataFetcher
from cryptvault.visualization.pattern_overlay import PatternOverlay


def create_sample_chart(symbol='BTC', days=60):
    """Create a sample candlestick chart with pattern overlays."""
    
    print(f"Fetching data for {symbol}...")
    
    # Fetch data
    fetcher = PackageDataFetcher()
    data = fetcher.fetch_historical_data(symbol, days=days, interval='1d')
    
    if not data or len(data.data) < 2:
        print("Error: Could not fetch data")
        return
    
    # Analyze patterns
    print("Analyzing patterns...")
    analyzer = PatternAnalyzer()
    results = analyzer.analyze_dataframe(data)
    
    if not results['success']:
        print(f"Error: {results.get('error')}")
        return
    
    patterns = results.get('patterns', [])
    print(f"Found {len(patterns)} patterns")
    
    # Extract price data
    dates = [point.timestamp for point in data.data]
    opens = [point.open for point in data.data]
    highs = [point.high for point in data.data]
    lows = [point.low for point in data.data]
    closes = [point.close for point in data.data]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')
    ax.set_facecolor('white')
    
    # Plot candlesticks (simple version)
    for i in range(len(dates)):
        color = 'green' if closes[i] >= opens[i] else 'red'
        
        # Wick
        ax.plot([dates[i], dates[i]], [lows[i], highs[i]], 
               color='gray', linewidth=1)
        
        # Body
        body_height = abs(closes[i] - opens[i])
        body_bottom = min(opens[i], closes[i])
        ax.bar(dates[i], body_height, bottom=body_bottom, 
              width=0.6, color=color, alpha=0.7)
    
    # Create pattern overlay
    overlay = PatternOverlay(ax)
    
    # Draw each pattern
    print("\nDrawing patterns:")
    for i, pattern in enumerate(patterns[:5], 1):  # Top 5 patterns
        print(f"  {i}. {pattern.get('type')} - {pattern.get('confidence')}")
        overlay.draw_pattern(pattern, dates, opens, highs, lows, closes)
    
    # Formatting
    ax.set_title(f'{symbol} - Pattern Analysis', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()


def main():
    """Main function."""
    print("=" * 60)
    print("Pattern Overlay Example")
    print("=" * 60)
    print()
    
    # Example 1: Bitcoin
    print("Example 1: Bitcoin Analysis")
    print("-" * 60)
    create_sample_chart('BTC', days=60)
    
    # Example 2: Apple Stock
    print("\nExample 2: Apple Stock Analysis")
    print("-" * 60)
    create_sample_chart('AAPL', days=90)


if __name__ == '__main__':
    main()
