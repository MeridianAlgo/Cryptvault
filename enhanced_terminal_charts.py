#!/usr/bin/env python3
"""
Enhanced CryptVault Terminal Charts
Advanced ASCII charts with comprehensive pattern visualization
"""

import sys
import os
import numpy as np
from datetime import datetime, timedelta
import argparse

# Add CryptVault to path
sys.path.append('.')

from cryptvault.analyzer import PatternAnalyzer
from cryptvault.data.package_fetcher import PackageDataFetcher

class EnhancedTerminalCharts:
    """Enhanced terminal-based charting with pattern visualization"""
    
    def __init__(self):
        self.analyzer = PatternAnalyzer()
        self.data_fetcher = PackageDataFetcher()
        
        # Enhanced pattern symbols and colors
        self.pattern_symbols = {
            'Double Bottom': '⩗',
            'Double Top': '⩘', 
            'Triple Bottom': '⫸',
            'Triple Top': '⫷',
            'Head and Shoulders': '⩙',
            'Inverse Head and Shoulders': '⩚',
            'Ascending Triangle': '△',
            'Descending Triangle': '▽',
            'Expanding Triangle': '◇',
            'Symmetrical Triangle': '◊',
            'Rising Wedge': '⟋',
            'Falling Wedge': '⟍',
            'Rectangle': '▭',
            'Flag': '⚑',
            'Pennant': '⚐',
            'Cup and Handle': '⌒',
            'Bullish Divergence': '↗',
            'Bearish Divergence': '↘',
            'Hidden Bullish Divergence': '⤴',
            'Hidden Bearish Divergence': '⤵',
            'ABCD': 'A',
            'Gartley': 'G',
            'Butterfly': 'B',
            'Bat': 'b',
            'Crab': 'C',
            'Shark': 'S',
            'Cypher': 'Y',
            'Three Drives': '3',
            'AB=CD': '=',
            'Falling Channel': '║',
            'Rising Channel': '║',
            'Support': '─',
            'Resistance': '─',
            'Breakout': '⚡',
            'Breakdown': '⚡'
        }
        
        # Pattern confidence indicators
        self.confidence_indicators = {
            'high': '●',      # 80%+
            'med-high': '◐',  # 60-79%
            'medium': '◑',    # 40-59%
            'low': '○'        # <40%
        }
    
    def get_confidence_level(self, confidence_str):
        """Get confidence level from percentage string"""
        try:
            confidence = float(confidence_str.rstrip('%'))
            if confidence >= 80:
                return 'high'
            elif confidence >= 60:
                return 'med-high'
            elif confidence >= 40:
                return 'medium'
            else:
                return 'low'
        except:
            return 'low'
    
    def create_enhanced_chart(self, data, patterns, symbol, width=70, height=20):
        """Create enhanced ASCII chart with pattern overlays"""
        if not data or len(data.data) < 2:
            return "Insufficient data for charting"
        
        # Extract price data
        prices = [point.close for point in data.data]
        volumes = [point.volume for point in data.data]
        dates = [point.timestamp for point in data.data]
        
        # Calculate price range
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = max_price * 0.01  # 1% range for flat prices
        
        # Create chart grid
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Plot price line
        for i in range(len(prices) - 1):
            x1 = int((i / (len(prices) - 1)) * (width - 1))
            x2 = int(((i + 1) / (len(prices) - 1)) * (width - 1))
            
            y1 = int(((prices[i] - min_price) / price_range) * (height - 1))
            y2 = int(((prices[i + 1] - min_price) / price_range) * (height - 1))
            
            # Ensure coordinates are within bounds
            y1 = max(0, min(height - 1, y1))
            y2 = max(0, min(height - 1, y2))
            x1 = max(0, min(width - 1, x1))
            x2 = max(0, min(width - 1, x2))
            
            # Draw line segments
            if x1 == x2:
                # Vertical line
                start_y, end_y = (y1, y2) if y1 <= y2 else (y2, y1)
                for y in range(start_y, end_y + 1):
                    if 0 <= y < height:
                        chart[height - 1 - y][x1] = '│'
            else:
                # Diagonal/horizontal line
                steps = abs(x2 - x1) + abs(y2 - y1)
                if steps > 0:
                    for step in range(steps + 1):
                        x = x1 + int((x2 - x1) * step / steps)
                        y = y1 + int((y2 - y1) * step / steps)
                        if 0 <= x < width and 0 <= y < height:
                            # Choose appropriate character
                            if abs(y2 - y1) > abs(x2 - x1):
                                char = '│' if y2 > y1 else '│'
                            elif y2 > y1:
                                char = '▲'
                            elif y2 < y1:
                                char = '▼'
                            else:
                                char = '─'
                            chart[height - 1 - y][x] = char
        
        # Add pattern overlays
        pattern_overlay = self.create_pattern_overlay(patterns, prices, dates, width, height, min_price, price_range)
        
        # Merge pattern overlay with chart
        for y in range(height):
            for x in range(width):
                if pattern_overlay[y][x] != ' ':
                    chart[y][x] = pattern_overlay[y][x]
        
        # Convert chart to string
        chart_lines = []
        
        # Add price labels on the left
        for i, row in enumerate(chart):
            price_at_row = min_price + (price_range * (height - 1 - i) / (height - 1))
            price_label = f"{price_at_row:8.2f}"
            chart_lines.append(f"{price_label} │{''.join(row)}│")
        
        # Add bottom border and date labels
        chart_lines.append(" " * 9 + "└" + "─" * width + "┘")
        
        # Add date labels
        start_date = dates[0].strftime("%m/%d %H:%M") if dates else "Start"
        end_date = dates[-1].strftime("%m/%d %H:%M") if dates else "End"
        date_line = " " * 10 + start_date + " " * (width - len(start_date) - len(end_date)) + end_date
        chart_lines.append(date_line)
        
        return '\n'.join(chart_lines)
    
    def create_pattern_overlay(self, patterns, prices, dates, width, height, min_price, price_range):
        """Create pattern overlay for the chart"""
        overlay = [[' ' for _ in range(width)] for _ in range(height)]
        
        if not patterns:
            return overlay
        
        # Sort patterns by confidence (highest first)
        sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
        
        for i, pattern in enumerate(sorted_patterns[:8]):  # Show top 8 patterns
            pattern_type = pattern.get('type', 'Unknown')
            confidence = pattern.get('confidence', '0%')
            
            # Get pattern symbol
            symbol = self.pattern_symbols.get(pattern_type, '*')
            confidence_level = self.get_confidence_level(confidence)
            confidence_symbol = self.confidence_indicators[confidence_level]
            
            # Try to place pattern markers
            if 'start_index' in pattern and 'end_index' in pattern:
                start_idx = max(0, min(pattern['start_index'], len(prices) - 1))
                end_idx = max(0, min(pattern['end_index'], len(prices) - 1))
                
                # Calculate positions
                start_x = int((start_idx / (len(prices) - 1)) * (width - 1))
                end_x = int((end_idx / (len(prices) - 1)) * (width - 1))
                
                # Place pattern markers
                for x in range(start_x, min(end_x + 1, width)):
                    # Place at different heights to avoid overlap
                    marker_y = (i % 3) + (height // 4) * (2 - (i % 3))
                    marker_y = max(0, min(height - 1, marker_y))
                    
                    if x < width and overlay[marker_y][x] == ' ':
                        if x == start_x:
                            overlay[marker_y][x] = symbol
                        elif x == end_x:
                            overlay[marker_y][x] = confidence_symbol
                        elif (x - start_x) % 3 == 0:  # Sparse markers
                            overlay[marker_y][x] = '┊' if 'Harmonic' in pattern_type else '│'
            else:
                # Place single marker in middle of chart
                mid_x = width // 2
                marker_y = height // 2 + (i % 3) - 1
                marker_y = max(0, min(height - 1, marker_y))
                
                if overlay[marker_y][mid_x] == ' ':
                    overlay[marker_y][mid_x] = symbol + confidence_symbol
        
        return overlay
    
    def format_pattern_list(self, patterns):
        """Format pattern list with enhanced details"""
        if not patterns:
            return "No patterns detected."
        
        # Group patterns by type
        pattern_groups = {}
        for pattern in patterns:
            ptype = pattern.get('type', 'Unknown')
            if ptype not in pattern_groups:
                pattern_groups[ptype] = []
            pattern_groups[ptype].append(pattern)
        
        # Sort by confidence
        sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
        
        output = []
        output.append("Detected Patterns:")
        output.append("─" * 60)
        
        for i, pattern in enumerate(sorted_patterns[:12], 1):  # Show top 12 patterns
            ptype = pattern.get('type', 'Unknown')
            confidence = pattern.get('confidence', '0%')
            
            # Get symbols
            pattern_symbol = self.pattern_symbols.get(ptype, '*')
            confidence_level = self.get_confidence_level(confidence)
            confidence_symbol = self.confidence_indicators[confidence_level]
            
            # Pattern classification
            if any(word in ptype for word in ['Bullish', 'Bottom', 'Ascending', 'Rising']):
                classification = "[Bullish]"
                bar_color = "██████████"
            elif any(word in ptype for word in ['Bearish', 'Top', 'Descending', 'Falling']):
                classification = "[Bearish]"
                bar_color = "██████████"
            elif 'Divergence' in ptype:
                classification = "[Divergence]"
                bar_color = "██████████"
            elif any(word in ptype for word in ['Triangle', 'Wedge', 'Rectangle']):
                classification = "[Continuation]"
                bar_color = "██████████"
            else:
                classification = "[Neutral]"
                bar_color = "██████████"
            
            # Format confidence bar
            conf_value = float(confidence.rstrip('%'))
            filled_bars = int(conf_value / 10)
            conf_bar = "█" * filled_bars + "░" * (10 - filled_bars)
            
            output.append(f" {i:2d}. {pattern_symbol} {ptype:<25} {classification:<12} [{conf_bar}] {confidence:>6} {confidence_symbol}")
            
            # Add target price if available
            if 'target_price' in pattern:
                output.append(f"     Target: ${pattern['target_price']:.2f}")
            
            # Add description if available
            if 'description' in pattern and len(pattern['description']) > 10:
                desc = pattern['description'][:50] + "..." if len(pattern['description']) > 50 else pattern['description']
                output.append(f"     {desc}")
        
        output.append("")
        output.append("Confidence: ● High (80%+)  ◐ Med-High (60%+)  ◑ Medium (40%+)  ○ Low (<40%)")
        output.append("Boundaries: │ Geometric  ┊ Harmonic  ┆ Candlestick")
        
        return '\n'.join(output)
    
    def analyze_and_chart(self, symbol, days=60, interval='1d'):
        """Analyze cryptocurrency and create enhanced chart"""
        print(f"🚀 Enhanced CryptVault Analysis - {symbol.upper()}")
        print("=" * 70)
        
        try:
            # Perform analysis
            print(f"Analyzing {symbol.upper()} with {days} days of {interval} data...")
            results = self.analyzer.analyze_ticker(symbol, days=days, interval=interval)
            
            if not results['success']:
                print(f"❌ Analysis failed: {results['error']}")
                if 'suggestions' in results:
                    print("\n💡 Suggestions:")
                    for suggestion in results['suggestions']:
                        print(f"  • {suggestion}")
                return False
            
            # Get data from results
            patterns = results.get('patterns', [])
            ml_predictions = results.get('ml_predictions', {})
            ticker_info = results.get('ticker_info', {})
            existing_chart = results.get('chart', '')
            
            print(f"Debug: Available result keys: {list(results.keys())}")
            
            # Use existing chart from analysis results
            if existing_chart:
                print("📊 Enhanced Chart with Pattern Overlays:")
                print(existing_chart)
                print()
            else:
                print("❌ No chart data available")
                return False
            
            # Display basic info
            current_price = ticker_info.get('current_price', 0)
            data_summary = results.get('data_summary', {})
            data_points_count = data_summary.get('total_points', 'Unknown')
            
            print(f"💰 Current Price: ${current_price:,.2f}")
            print(f"📊 Data Points: {data_points_count}")
            print(f"🔍 Patterns Found: {len(patterns)}")
            print(f"⏱️  Analysis Time: {results.get('analysis_time_seconds', 0):.2f}s")
            
            # Display ML predictions
            if ml_predictions and 'trend_forecast' in ml_predictions:
                trend = ml_predictions['trend_forecast']
                print(f"🧠 ML Trend: {trend.get('trend_7d', 'Unknown')} ({trend.get('trend_strength', 'Unknown')})")
            
            print()
            
            # The chart is already displayed above, so we skip the custom chart creation
            
            # Display pattern analysis
            pattern_analysis = self.format_pattern_list(patterns)
            print(pattern_analysis)
            
            # Display additional insights
            if patterns:
                print(f"\n📈 Pattern Insights:")
                bullish_patterns = [p for p in patterns if any(word in p.get('type', '') for word in ['Bullish', 'Bottom', 'Ascending'])]
                bearish_patterns = [p for p in patterns if any(word in p.get('type', '') for word in ['Bearish', 'Top', 'Descending'])]
                
                print(f"   • Bullish signals: {len(bullish_patterns)}")
                print(f"   • Bearish signals: {len(bearish_patterns)}")
                
                if bullish_patterns and len(bullish_patterns) > len(bearish_patterns):
                    print("   • Overall bias: 🟢 BULLISH")
                elif bearish_patterns and len(bearish_patterns) > len(bullish_patterns):
                    print("   • Overall bias: 🔴 BEARISH")
                else:
                    print("   • Overall bias: 🟡 NEUTRAL")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced CryptVault Terminal Charts")
    parser.add_argument('symbol', nargs='?', default='BTC', help='Cryptocurrency symbol')
    parser.add_argument('days', nargs='?', type=int, default=60, help='Number of days')
    parser.add_argument('interval', nargs='?', default='1d', help='Data interval')
    parser.add_argument('--multiple', '-m', nargs='+', help='Analyze multiple symbols')
    
    args = parser.parse_args()
    
    charts = EnhancedTerminalCharts()
    
    if args.multiple:
        # Analyze multiple symbols
        for symbol in args.multiple:
            charts.analyze_and_chart(symbol, args.days, args.interval)
            print("\n" + "=" * 70 + "\n")
    else:
        # Analyze single symbol
        charts.analyze_and_chart(args.symbol, args.days, args.interval)

if __name__ == "__main__":
    main()