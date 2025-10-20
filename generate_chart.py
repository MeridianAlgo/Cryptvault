"""
Generate Candlestick Charts with Pattern Overlays
Usage: python generate_chart.py SYMBOL [--days DAYS] [--interval INTERVAL] [--save FILENAME]

Examples:
    python generate_chart.py BTC
    python generate_chart.py AAPL --days 60 --interval 1d
    python generate_chart.py TSLA --days 90 --save tesla_chart.png
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import argparse
import sys
from datetime import datetime

# Import CryptVault components
from cryptvault.analyzer import PatternAnalyzer
from cryptvault.data.package_fetcher import PackageDataFetcher
from cryptvault.visualization.pattern_overlay import PatternOverlay


def plot_candlesticks(ax, dates, opens, highs, lows, closes):
    """Plot candlestick chart."""
    from matplotlib.patches import Rectangle
    
    # Calculate colors for each candlestick
    colors = ['#00ff88' if close >= open_price else '#ff4444' 
              for open_price, close in zip(opens, closes)]
    
    # Plot candlesticks
    for i, (date, open_price, high, low, close, color) in enumerate(
        zip(dates, opens, highs, lows, closes, colors)):
        
        # Draw the wick (high-low line)
        ax.plot([date, date], [low, high], color='#666666', linewidth=1, alpha=0.8)
        
        # Draw the body (rectangle)
        body_height = abs(close - open_price)
        body_bottom = min(open_price, close)
        
        # Create rectangle for candlestick body
        rect = Rectangle((mdates.date2num(date) - 0.3, body_bottom), 0.6, body_height, 
                        facecolor=color, edgecolor=color, alpha=0.8, linewidth=1)
        ax.add_patch(rect)


def plot_volume(ax, dates, volumes, closes):
    """Plot volume bars."""
    if not volumes or all(v == 0 for v in volumes):
        return
    
    # Calculate colors based on price movement
    colors = []
    for i in range(len(closes)):
        if i == 0:
            colors.append('#666666')
        else:
            colors.append('#00ff88' if closes[i] >= closes[i-1] else '#ff4444')
    
    # Plot volume bars
    ax.bar(dates, volumes, color=colors, alpha=0.6, width=0.8)
    
    # Format volume axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))


def generate_chart(symbol, days=30, interval='1d', save_path=None):
    """
    Generate candlestick chart with pattern overlays.
    
    Args:
        symbol: Stock or crypto ticker symbol
        days: Number of days of historical data
        interval: Data interval (1h, 4h, 1d, 1w)
        save_path: Optional path to save chart image
    """
    print(f"Analyzing {symbol}...")
    
    # Initialize analyzer and data fetcher
    analyzer = PatternAnalyzer()
    data_fetcher = PackageDataFetcher()
    
    # Fetch data
    print(f"Fetching {days} days of data...")
    raw_data = data_fetcher.fetch_historical_data(symbol, days=days, interval=interval)
    
    if not raw_data or len(raw_data.data) < 2:
        print("Error: Insufficient data for charting")
        return
    
    # Analyze patterns
    print("Detecting patterns...")
    results = analyzer.analyze_dataframe(raw_data)
    
    if not results['success']:
        print(f"Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    patterns = results.get('patterns', [])
    print(f"Found {len(patterns)} patterns")
    
    # Extract data for plotting
    data_points = raw_data.data
    dates = [point.timestamp for point in data_points]
    opens = [point.open for point in data_points]
    highs = [point.high for point in data_points]
    lows = [point.low for point in data_points]
    closes = [point.close for point in data_points]
    volumes = [getattr(point, 'volume', 0) or 0 for point in data_points]
    
    # Create figure with dark theme
    fig = plt.figure(figsize=(16, 10), facecolor='#0a0e13')
    try:
        fig.canvas.manager.set_window_title(f'{symbol.upper()} - Pattern Analysis')
    except:
        pass
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)
    
    # Price chart
    ax_price = fig.add_subplot(gs[0])
    ax_price.set_facecolor('#0f1419')
    ax_price.tick_params(colors='#e6e8eb', labelsize=10)
    ax_price.grid(True, color='#1e2329', alpha=0.4, linewidth=0.5)
    
    # Volume chart
    ax_vol = fig.add_subplot(gs[1], sharex=ax_price)
    ax_vol.set_facecolor('#0f1419')
    ax_vol.tick_params(colors='#e6e8eb', labelsize=10)
    ax_vol.grid(True, color='#1e2329', alpha=0.4, linewidth=0.5)
    
    # Style spines
    for ax in (ax_price, ax_vol):
        for spine in ax.spines.values():
            spine.set_color('#2a2f3a')
            spine.set_linewidth(0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    # Plot candlesticks
    print("Plotting candlesticks...")
    plot_candlesticks(ax_price, dates, opens, highs, lows, closes)
    
    # Plot volume
    print("Plotting volume...")
    plot_volume(ax_vol, dates, volumes, closes)
    
    # Overlay patterns
    if patterns:
        print(f"Overlaying {len(patterns)} patterns...")
        overlay = PatternOverlay(ax_price)
        
        for i, pattern in enumerate(patterns[:10], 1):  # Limit to top 10 patterns
            print(f"  {i}. {pattern.get('type', 'Unknown')} - {pattern.get('confidence', 'N/A')}")
            overlay.draw_pattern(pattern, dates, opens, highs, lows, closes)
    
    # Add price line
    ax_price.plot(dates, closes, color='#00d4ff', linewidth=1.5, alpha=0.7, label='Close Price')
    
    # Calculate price change
    price_change = ((closes[-1] - closes[0]) / closes[0]) * 100
    change_symbol = "▲" if price_change >= 0 else "▼"
    change_color = '#00ff88' if price_change >= 0 else '#ff4444'
    
    # Add current price indicator
    current_price = closes[-1]
    ax_price.axhline(y=current_price, color=change_color, linestyle='--', 
                    alpha=0.6, linewidth=1.5)
    ax_price.annotate(f'${current_price:.2f}', 
                     xy=(dates[-1], current_price),
                     xytext=(10, 0), textcoords='offset points',
                     color=change_color, fontweight='bold', fontsize=11,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor=change_color, alpha=0.2))
    
    # Titles and labels
    title = f'{symbol.upper()} - Pattern Analysis\n'
    title += f'${current_price:.2f} {change_symbol} {abs(price_change):.2f}%'
    ax_price.set_title(title, fontsize=16, fontweight='bold', color='#00d4ff', pad=20)
    ax_price.set_ylabel('Price ($)', fontsize=12, color='#e6e8eb', fontweight='bold')
    ax_vol.set_ylabel('Volume', fontsize=10, color='#e6e8eb', fontweight='bold')
    ax_vol.set_xlabel('Date', fontsize=12, color='#e6e8eb', fontweight='bold')
    
    # Format x-axis dates
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax_price.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    plt.setp(ax_vol.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Hide duplicate x labels on top axis
    ax_price.tick_params(labelbottom=False)
    
    # Add legend
    ax_price.legend(loc='upper left', frameon=True, fancybox=True, shadow=True,
                   framealpha=0.9, facecolor='#1a1f2e', edgecolor='#2a2f3a', fontsize=9)
    
    # Add pattern summary text box
    if patterns:
        summary_text = f"Patterns Detected: {len(patterns)}\n"
        bullish = sum(1 for p in patterns if p.get('is_bullish', False))
        bearish = sum(1 for p in patterns if p.get('is_bearish', False))
        summary_text += f"Bullish: {bullish} | Bearish: {bearish}"
        
        ax_price.text(0.02, 0.98, summary_text, transform=ax_price.transAxes,
                     fontsize=10, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='#1a1f2e', alpha=0.9, edgecolor='#2a2f3a'),
                     color='#e6e8eb')
    
    # Tight layout
    fig.tight_layout()
    
    # Show or save
    if save_path:
        print(f"Saving chart to {save_path}...")
        plt.savefig(save_path, dpi=150, facecolor='#0a0e13', edgecolor='none', bbox_inches='tight')
        print(f"Chart saved successfully!")
        plt.close()
    else:
        print("Opening interactive chart window...")
        print("Use the toolbar to zoom, pan, and navigate")
        print("Close the window when done")
        plt.show()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate candlestick charts with pattern overlays',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Display in interactive window (default)
  python generate_chart.py BTC
  python generate_chart.py AAPL --days 60
  python generate_chart.py TSLA --days 90
  
  # Save to file instead
  python generate_chart.py GOOGL --days 120 --save google.png
  python generate_chart.py SPY --days 180 --save sp500.png

Supported intervals: 1h, 4h, 1d, 1w

The chart will open in an interactive matplotlib window where you can:
  - Zoom in/out
  - Pan around
  - Save manually using the toolbar
  - Close the window to exit
        """
    )
    
    parser.add_argument('symbol', type=str, help='Stock or crypto ticker symbol (e.g., BTC, AAPL, TSLA)')
    parser.add_argument('--days', type=int, default=30, help='Number of days of historical data (default: 30)')
    parser.add_argument('--interval', type=str, default='1d', choices=['1h', '4h', '1d', '1w'],
                       help='Data interval (default: 1d)')
    parser.add_argument('--save', type=str, help='Optional: Save chart to file (default: display in window)')
    
    args = parser.parse_args()
    
    # Generate chart
    try:
        generate_chart(args.symbol, args.days, args.interval, args.save)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
