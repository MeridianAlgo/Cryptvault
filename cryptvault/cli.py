"""Command-line interface for the crypto chart pattern analyzer."""

import argparse
import sys
import os
from typing import Optional

from .analyzer import PatternAnalyzer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Crypto Chart Pattern Analyzer - Terminal-based pattern recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze CSV file
  python -m crypto_chart_analyzer.cli --csv data.csv
  
  # Analyze JSON file with high sensitivity
  python -m crypto_chart_analyzer.cli --json data.json --sensitivity 0.8
  
  # Analyze with custom chart size
  python -m crypto_chart_analyzer.cli --csv data.csv --width 120 --height 30
  
  # Show pattern details
  python -m crypto_chart_analyzer.cli --csv data.csv --details 0
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--csv', type=str, help='CSV file path with OHLCV data')
    input_group.add_argument('--json', type=str, help='JSON file path with OHLCV data')
    
    # Analysis options
    parser.add_argument('--sensitivity', type=float, default=0.5, 
                       help='Pattern detection sensitivity (0.0-1.0, default: 0.5)')
    parser.add_argument('--min-confidence', type=float, default=0.3,
                       help='Minimum confidence threshold (0.0-1.0, default: 0.3)')
    
    # Display options
    parser.add_argument('--width', type=int, default=100,
                       help='Chart width in characters (default: 100)')
    parser.add_argument('--height', type=int, default=25,
                       help='Chart height in characters (default: 25)')
    parser.add_argument('--no-colors', action='store_true',
                       help='Disable colored output')
    parser.add_argument('--details', type=int, metavar='N',
                       help='Show detailed info for pattern N (0-based index)')
    
    # Output options
    parser.add_argument('--save', type=str, metavar='FILE',
                       help='Save analysis results to file')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress chart output, show only summary')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.sensitivity < 0.0 or args.sensitivity > 1.0:
        print("Error: Sensitivity must be between 0.0 and 1.0")
        sys.exit(1)
    
    if args.min_confidence < 0.0 or args.min_confidence > 1.0:
        print("Error: Min confidence must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = PatternAnalyzer()
    analyzer.set_sensitivity(args.sensitivity)
    analyzer.set_min_confidence(args.min_confidence)
    analyzer.set_chart_dimensions(args.width, args.height)
    analyzer.enable_colors(not args.no_colors)
    
    # Load and analyze data
    try:
        if args.csv:
            if not os.path.exists(args.csv):
                print(f"Error: CSV file '{args.csv}' not found")
                sys.exit(1)
            
            with open(args.csv, 'r') as f:
                data = f.read()
            
            print(f"Analyzing CSV file: {args.csv}")
            result = analyzer.analyze_from_csv(data, args.sensitivity)
        
        elif args.json:
            if not os.path.exists(args.json):
                print(f"Error: JSON file '{args.json}' not found")
                sys.exit(1)
            
            with open(args.json, 'r') as f:
                data = f.read()
            
            print(f"Analyzing JSON file: {args.json}")
            result = analyzer.analyze_from_json(data, args.sensitivity)
        
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    # Handle analysis results
    if not result['success']:
        print(f"Analysis failed: {result['error']}")
        
        if 'validation_errors' in result:
            print("\nValidation Errors:")
            for error in result['validation_errors']:
                print(f"  • {error}")
        
        if 'suggestions' in result:
            print("\nSuggestions:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
        
        sys.exit(1)
    
    # Display results
    display_results(result, args, analyzer)
    
    # Save results if requested
    if args.save:
        save_results(result, args.save)


def display_results(result: dict, args: argparse.Namespace, analyzer: PatternAnalyzer):
    """Display analysis results."""
    
    # Show summary
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    data_summary = result['data_summary']
    print(f"Symbol: {data_summary['symbol']}")
    print(f"Timeframe: {data_summary['timeframe']}")
    print(f"Data Points: {data_summary['data_points']}")
    print(f"Date Range: {data_summary['date_range'][0].strftime('%Y-%m-%d %H:%M')} to {data_summary['date_range'][1].strftime('%Y-%m-%d %H:%M')}")
    print(f"Price Range: ${data_summary['price_range'][0]:.2f} - ${data_summary['price_range'][1]:.2f}")
    print(f"Analysis Time: {result['analysis_time_seconds']:.2f} seconds")
    
    # Show pattern summary
    pattern_summary = result['pattern_summary']
    print(f"\nPatterns Found: {pattern_summary['total']}")
    
    if pattern_summary['total'] > 0:
        print(f"Average Confidence: {pattern_summary['average_confidence']}")
        print(f"Highest Confidence: {pattern_summary['highest_confidence']}")
        
        sentiment = pattern_summary['sentiment']
        print(f"Sentiment: {sentiment['bullish']} Bullish, {sentiment['bearish']} Bearish, {sentiment['neutral']} Neutral")
        
        if pattern_summary['most_common_category']:
            print(f"Most Common: {pattern_summary['most_common_category']}")
    
    # Show technical indicators
    if 'technical_indicators' in result:
        indicators = result['technical_indicators']
        print(f"\nTechnical Indicators:")
        
        if 'rsi' in indicators and indicators['rsi']['current']:
            rsi_status = "Overbought" if indicators['rsi']['overbought'] else "Oversold" if indicators['rsi']['oversold'] else "Normal"
            print(f"  RSI: {indicators['rsi']['current']:.1f} ({rsi_status})")
        
        if 'macd' in indicators and indicators['macd']['current_macd']:
            macd_status = "Bullish" if indicators['macd']['bullish_crossover'] else "Bearish"
            print(f"  MACD: {indicators['macd']['current_macd']:.4f} ({macd_status})")
    
    # Show recommendations
    if result['recommendations']:
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        for rec in result['recommendations']:
            print(f"  {rec}")
    
    # Show detailed pattern info if requested
    if args.details is not None:
        patterns = result['patterns']
        if 0 <= args.details < len(patterns):
            print(f"\n{'='*60}")
            print(f"PATTERN DETAILS #{args.details}")
            print(f"{'='*60}")
            # Note: This would need the actual DetectedPattern objects, not the formatted dict
            print("Pattern details would be shown here")
        else:
            print(f"\nError: Pattern index {args.details} out of range (0-{len(patterns)-1})")
    
    # Show patterns list
    if result['patterns'] and not args.quiet:
        print(f"\n{'='*60}")
        print("DETECTED PATTERNS")
        print(f"{'='*60}")
        
        for i, pattern in enumerate(result['patterns']):
            confidence_bar = "█" * int(pattern['confidence_raw'] * 10)
            confidence_bar += "░" * (10 - len(confidence_bar))
            
            sentiment_icon = "📈" if pattern['is_bullish'] else "📉" if pattern['is_bearish'] else "⚖️"
            reversal_icon = "🔄" if pattern['is_reversal'] else "➡️"
            
            print(f"{i:2d}. {sentiment_icon}{reversal_icon} {pattern['type']}")
            print(f"     Confidence: [{confidence_bar}] {pattern['confidence']}")
            print(f"     Duration: {pattern['duration_hours']:.1f} hours")
            print(f"     Category: {pattern['category']}")
            if pattern['volume_confirmation']:
                print(f"     Volume: ✅ Confirmed")
            else:
                print(f"     Volume: ⚠️ Weak")
            print()
    
    # Show chart if not quiet
    if not args.quiet and 'chart' in result:
        print(f"\n{'='*60}")
        print("PRICE CHART")
        print(f"{'='*60}")
        print(result['chart'])


def save_results(result: dict, filename: str):
    """Save analysis results to file."""
    import json
    from datetime import datetime
    
    # Convert datetime objects to strings for JSON serialization
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    try:
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=json_serializer)
        print(f"\nResults saved to: {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")


def show_sample_data():
    """Show sample data formats."""
    print("Sample CSV format:")
    print("timestamp,open,high,low,close,volume,symbol,timeframe")
    print("2023-01-01 12:00:00,100.0,105.0,95.0,102.0,1000.0,BTC,1h")
    print("2023-01-01 13:00:00,102.0,108.0,98.0,105.0,1200.0,BTC,1h")
    print()
    print("Sample JSON format:")
    print("""[
  {
    "timestamp": "2023-01-01 12:00:00",
    "open": 100.0,
    "high": 105.0,
    "low": 95.0,
    "close": 102.0,
    "volume": 1000.0,
    "symbol": "BTC",
    "timeframe": "1h"
  }
]""")


if __name__ == '__main__':
    main()