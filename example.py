#!/usr/bin/env python3
"""
Example usage of the Crypto Chart Pattern Analyzer.

This script demonstrates how to use the analyzer with sample data.
"""

from datetime import datetime, timedelta
from crypto_chart_analyzer.analyzer import PatternAnalyzer
from crypto_chart_analyzer.data.models import PricePoint, PriceDataFrame


def create_sample_data():
    """Create sample price data with patterns."""
    base_time = datetime(2023, 1, 1, 12, 0, 0)
    
    # Create data that forms an ascending triangle pattern
    prices = [
        100, 105, 102, 108, 104, 110, 106, 109, 107, 110,
        108, 109, 109, 110, 109.5, 110, 110, 109.8, 110.2, 111,
        113, 115, 112, 118, 114, 120, 116, 122, 118, 125
    ]
    
    data = []
    for i, price in enumerate(prices):
        timestamp = base_time + timedelta(hours=i)
        
        # Create realistic OHLC data
        high = price + (2 if i < 20 else 3)  # Breakout has higher volatility
        low = price - (1.5 if i < 20 else 1)
        close = price + 0.5
        volume = 1000 - (i * 15) if i < 20 else 1500 + (i * 50)  # Volume increases on breakout
        
        point = PricePoint(
            timestamp=timestamp,
            open=price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        data.append(point)
    
    return PriceDataFrame(data=data, symbol="BTC", timeframe="1h")


def main():
    """Run the example analysis."""
    print("Crypto Chart Pattern Analyzer - Example")
    print("=" * 50)
    
    # Create sample data
    print("Creating sample data with ascending triangle pattern...")
    sample_data = create_sample_data()
    
    # Initialize analyzer
    analyzer = PatternAnalyzer()
    analyzer.set_chart_dimensions(100, 25)
    
    # Perform analysis
    print("Analyzing patterns...")
    result = analyzer.analyze_dataframe(sample_data, sensitivity=0.6)
    
    if not result['success']:
        print(f"Analysis failed: {result['error']}")
        return
    
    # Display results
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS")
    print(f"{'='*60}")
    
    # Summary
    data_summary = result['data_summary']
    print(f"Symbol: {data_summary['symbol']}")
    print(f"Data Points: {data_summary['data_points']}")
    print(f"Price Range: ${data_summary['price_range'][0]:.2f} - ${data_summary['price_range'][1]:.2f}")
    
    # Patterns
    pattern_summary = result['pattern_summary']
    print(f"\nPatterns Found: {pattern_summary['total']}")
    
    if pattern_summary['total'] > 0:
        print(f"Average Confidence: {pattern_summary['average_confidence']}")
        
        print(f"\nDetected Patterns:")
        for i, pattern in enumerate(result['patterns']):
            confidence_bar = "█" * int(pattern['confidence_raw'] * 10)
            confidence_bar += "░" * (10 - len(confidence_bar))
            
            sentiment = "📈 Bullish" if pattern['is_bullish'] else "📉 Bearish" if pattern['is_bearish'] else "⚖️ Neutral"
            
            print(f"{i+1}. {pattern['type']} - {sentiment}")
            print(f"   Confidence: [{confidence_bar}] {pattern['confidence']}")
            print(f"   Duration: {pattern['duration_hours']:.1f} hours")
            print()
    
    # Recommendations
    if result['recommendations']:
        print("Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
    
    # Chart
    print(f"\n{'='*60}")
    print("PRICE CHART")
    print(f"{'='*60}")
    print(result['chart'])
    
    print(f"\n{'='*60}")
    print("EXAMPLE COMPLETE")
    print(f"{'='*60}")
    print("To use with your own data:")
    print("1. Prepare CSV or JSON data with OHLCV format")
    print("2. Use: python -m crypto_chart_analyzer.cli --csv your_data.csv")
    print("3. Adjust sensitivity with --sensitivity 0.8 for more patterns")
    print("4. Use --help for all options")


if __name__ == '__main__':
    main()