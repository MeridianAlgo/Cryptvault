"""
Example: Custom Chart with Pattern Overlays

This example shows how to create a custom candlestick chart
and overlay detected patterns using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def plot_candlestick_with_patterns():
    """
    Create a candlestick chart with pattern overlays.
    
    This demonstrates the approach you mentioned:
    1. Use matplotlib to plot candlestick chart
    2. Overlay patterns with ax.plot(), ax.arrow(), or ax.fill_between()
    """
    
    # Sample OHLC data (replace with your cryptvault output)
    dates = pd.date_range('2023-01-01', periods=50)
    np.random.seed(42)
    
    # Generate realistic price data
    base_price = 100
    prices = [base_price]
    for _ in range(49):
        change = np.random.randn() * 2
        prices.append(prices[-1] + change)
    
    data = pd.DataFrame({
        'Open': prices,
        'High': [p + abs(np.random.randn() * 2) for p in prices],
        'Low': [p - abs(np.random.randn() * 2) for p in prices],
        'Close': [p + np.random.randn() * 1.5 for p in prices]
    }, index=dates)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 10), facecolor='#0a0e13')
    ax.set_facecolor('#0f1419')
    
    # Plot candlesticks
    width = 0.6
    width2 = 0.05
    
    up = data[data.Close >= data.Open]
    down = data[data.Close < data.Open]
    
    # Up candles (green)
    ax.bar(up.index, up.Close - up.Open, width, bottom=up.Open, 
          color='#00ff88', alpha=0.8, label='Up')
    ax.bar(up.index, up.High - up.Close, width2, bottom=up.Close, 
          color='#00ff88', alpha=0.8)
    ax.bar(up.index, up.Low - up.Open, width2, bottom=up.Open, 
          color='#00ff88', alpha=0.8)
    
    # Down candles (red)
    ax.bar(down.index, down.Open - down.Close, width, bottom=down.Close, 
          color='#ff4444', alpha=0.8, label='Down')
    ax.bar(down.index, down.High - down.Open, width2, bottom=down.Open, 
          color='#ff4444', alpha=0.8)
    ax.bar(down.index, down.Low - down.Close, width2, bottom=down.Close, 
          color='#ff4444', alpha=0.8)
    
    # Example 1: Overlay ascending triangle pattern
    # (Replace with cryptvault pattern output)
    triangle_start = data.index[10]
    triangle_end = data.index[30]
    
    # Resistance line (flat)
    resistance = data.High[10:31].max()
    ax.plot([triangle_start, triangle_end], [resistance, resistance], 
           'b--', linewidth=2, alpha=0.7, label='Resistance')
    
    # Support line (ascending)
    support_start = data.Low[10]
    support_end = data.Low[30]
    ax.plot([triangle_start, triangle_end], [support_start, support_end], 
           'g-', linewidth=2, alpha=0.7, label='Support')
    
    # Add pattern label
    mid_date = data.index[20]
    mid_price = (resistance + support_start) / 2
    ax.annotate('Ascending Triangle', 
               xy=(mid_date, mid_price),
               xytext=(0, 20), textcoords='offset points',
               ha='center', fontsize=10, color='#00d4ff', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7),
               arrowprops=dict(arrowstyle='->', color='#00d4ff'))
    
    # Example 2: Overlay support/resistance levels
    support_level = data.Low.min() + 2
    resistance_level = data.High.max() - 2
    
    ax.axhline(y=support_level, color='#00ff88', linestyle=':', 
              linewidth=1.5, alpha=0.6, label='Support Level')
    ax.axhline(y=resistance_level, color='#ff4444', linestyle=':', 
              linewidth=1.5, alpha=0.6, label='Resistance Level')
    
    # Example 3: Highlight a breakout area with fill_between
    breakout_start = data.index[35]
    breakout_end = data.index[45]
    breakout_low = data.Low[35:46].min()
    breakout_high = data.High[35:46].max()
    
    ax.fill_between([breakout_start, breakout_end], 
                   [breakout_low, breakout_low], 
                   [breakout_high, breakout_high],
                   color='yellow', alpha=0.2, label='Breakout Zone')
    
    # Example 4: Add arrow for trend direction
    trend_start_date = data.index[5]
    trend_end_date = data.index[25]
    trend_start_price = data.Close[5]
    trend_end_price = data.Close[25]
    
    ax.annotate('', xy=(trend_end_date, trend_end_price),
               xytext=(trend_start_date, trend_start_price),
               arrowprops=dict(arrowstyle='->', color='#8844ff', lw=2, alpha=0.7))
    
    ax.text(data.index[15], trend_start_price + 5, 'Uptrend', 
           color='#8844ff', fontsize=10, fontweight='bold')
    
    # Styling
    ax.tick_params(colors='#e6e8eb', labelsize=10)
    ax.grid(True, color='#1e2329', alpha=0.4, linewidth=0.5)
    
    for spine in ax.spines.values():
        spine.set_color('#2a2f3a')
        spine.set_linewidth(0.8)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Labels and title
    ax.set_title('Candlestick Chart with Pattern Overlays', 
                fontsize=16, fontweight='bold', color='#00d4ff', pad=20)
    ax.set_xlabel('Date', fontsize=12, color='#e6e8eb', fontweight='bold')
    ax.set_ylabel('Price ($)', fontsize=12, color='#e6e8eb', fontweight='bold')
    
    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#e6e8eb')
    
    # Legend
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True,
             framealpha=0.9, facecolor='#1a1f2e', edgecolor='#2a2f3a', 
             fontsize=9, labelcolor='#e6e8eb')
    
    plt.tight_layout()
    
    # Save or show
    # plt.savefig('chart.png', dpi=150, facecolor='#0a0e13')
    plt.show()


def plot_with_cryptvault_patterns():
    """
    Example showing how to integrate with CryptVault pattern detection.
    """
    from cryptvault.core.analyzer import PatternAnalyzer
    from cryptvault.data.package_fetcher import PackageDataFetcher
    
    # Fetch real data
    fetcher = PackageDataFetcher()
    data = fetcher.fetch_historical_data('BTC', days=60, interval='1d')
    
    if not data:
        print("Could not fetch data")
        return
    
    # Analyze patterns
    analyzer = PatternAnalyzer()
    results = analyzer.analyze_dataframe(data)
    
    if not results['success']:
        print(f"Analysis failed: {results.get('error')}")
        return
    
    # Extract data
    dates = [point.timestamp for point in data.data]
    opens = [point.open for point in data.data]
    highs = [point.high for point in data.data]
    lows = [point.low for point in data.data]
    closes = [point.close for point in data.data]
    
    # Create chart
    fig, ax = plt.subplots(figsize=(16, 10), facecolor='#0a0e13')
    ax.set_facecolor('#0f1419')
    
    # Plot candlesticks
    width = 0.6
    for i in range(len(dates)):
        color = '#00ff88' if closes[i] >= opens[i] else '#ff4444'
        
        # Wick
        ax.plot([dates[i], dates[i]], [lows[i], highs[i]], 
               color='#666666', linewidth=1, alpha=0.8)
        
        # Body
        body_height = abs(closes[i] - opens[i])
        body_bottom = min(opens[i], closes[i])
        rect = Rectangle((mdates.date2num(dates[i]) - 0.3, body_bottom), 
                        0.6, body_height, 
                        facecolor=color, edgecolor=color, alpha=0.8)
        ax.add_patch(rect)
    
    # Overlay patterns from CryptVault
    patterns = results.get('patterns', [])
    print(f"Found {len(patterns)} patterns")
    
    for pattern in patterns[:5]:  # Top 5 patterns
        pattern_type = pattern.get('type', '')
        key_levels = pattern.get('key_levels', {})
        
        print(f"Drawing pattern: {pattern_type}")
        
        # Draw support/resistance levels
        if 'support' in key_levels:
            ax.axhline(y=key_levels['support'], color='#00ff88', 
                      linestyle='--', linewidth=1.5, alpha=0.6)
        
        if 'resistance' in key_levels:
            ax.axhline(y=key_levels['resistance'], color='#ff4444', 
                      linestyle='--', linewidth=1.5, alpha=0.6)
        
        # Add pattern label
        if dates:
            mid_idx = len(dates) // 2
            mid_price = (max(highs) + min(lows)) / 2
            ax.annotate(pattern_type, 
                       xy=(dates[mid_idx], mid_price),
                       xytext=(0, 20), textcoords='offset points',
                       ha='center', fontsize=9, color='#00d4ff', 
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', 
                               facecolor='black', alpha=0.7))
    
    # Styling
    ax.tick_params(colors='#e6e8eb', labelsize=10)
    ax.grid(True, color='#1e2329', alpha=0.4, linewidth=0.5)
    
    for spine in ax.spines.values():
        spine.set_color('#2a2f3a')
    
    ax.set_title('BTC - CryptVault Pattern Analysis', 
                fontsize=16, fontweight='bold', color='#00d4ff', pad=20)
    ax.set_xlabel('Date', fontsize=12, color='#e6e8eb', fontweight='bold')
    ax.set_ylabel('Price ($)', fontsize=12, color='#e6e8eb', fontweight='bold')
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    print("Example 1: Custom Chart with Manual Pattern Overlays")
    print("=" * 60)
    plot_candlestick_with_patterns()
    
    print("\nExample 2: Chart with CryptVault Pattern Detection")
    print("=" * 60)
    plot_with_cryptvault_patterns()
