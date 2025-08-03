#!/usr/bin/env python3
"""
Advanced CryptVault Terminal Charts
Minimalist, colorful, professional crypto analysis with enhanced patterns
"""

import sys
import os
import numpy as np
import time
import threading
import argparse
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

# Add CryptVault to path
sys.path.append('.')

from cryptvault.analyzer import PatternAnalyzer
import logging

# Suppress INFO logs - only show warnings and errors
logging.getLogger('cryptvault').setLevel(logging.WARNING)

class AdvancedCryptoCharts:
    """Advanced minimalist terminal charts with enhanced patterns and time-based bias"""
    
    def __init__(self, verbose=False):
        self.analyzer = PatternAnalyzer()
        self.verbose = verbose
        
        # Enhanced pattern library with 50+ patterns
        self.patterns = {
            # Reversal Patterns
            'Double Bottom': {'symbol': '⩗', 'bias': 'bullish', 'strength': 0.8},
            'Double Top': {'symbol': '⩘', 'bias': 'bearish', 'strength': 0.8},
            'Triple Bottom': {'symbol': '⫸', 'bias': 'bullish', 'strength': 0.9},
            'Triple Top': {'symbol': '⫷', 'bias': 'bearish', 'strength': 0.9},
            'Head and Shoulders': {'symbol': '⩙', 'bias': 'bearish', 'strength': 0.85},
            'Inverse Head and Shoulders': {'symbol': '⩚', 'bias': 'bullish', 'strength': 0.85},
            'Cup and Handle': {'symbol': '⌒', 'bias': 'bullish', 'strength': 0.75},
            'Inverted Cup and Handle': {'symbol': '⌓', 'bias': 'bearish', 'strength': 0.75},
            'Rounding Bottom': {'symbol': '⌒', 'bias': 'bullish', 'strength': 0.7},
            'Rounding Top': {'symbol': '⌓', 'bias': 'bearish', 'strength': 0.7},
            'V-Bottom': {'symbol': 'V', 'bias': 'bullish', 'strength': 0.6},
            'Inverted V-Top': {'symbol': 'Λ', 'bias': 'bearish', 'strength': 0.6},
            
            # Triangle Patterns
            'Ascending Triangle': {'symbol': '△', 'bias': 'bullish', 'strength': 0.7},
            'Descending Triangle': {'symbol': '▽', 'bias': 'bearish', 'strength': 0.7},
            'Expanding Triangle': {'symbol': '◇', 'bias': 'neutral', 'strength': 0.5},
            'Symmetrical Triangle': {'symbol': '◊', 'bias': 'neutral', 'strength': 0.6},
            'Right Triangle': {'symbol': '⊿', 'bias': 'neutral', 'strength': 0.55},
            
            # Wedge Patterns
            'Rising Wedge': {'symbol': '⟋', 'bias': 'bearish', 'strength': 0.75},
            'Falling Wedge': {'symbol': '⟍', 'bias': 'bullish', 'strength': 0.75},
            'Rising Wedge Reversal': {'symbol': '⟋', 'bias': 'bearish', 'strength': 0.8},
            'Falling Wedge Reversal': {'symbol': '⟍', 'bias': 'bullish', 'strength': 0.8},
            
            # Channel Patterns
            'Rising Channel': {'symbol': '║', 'bias': 'bullish', 'strength': 0.6},
            'Falling Channel': {'symbol': '║', 'bias': 'bearish', 'strength': 0.6},
            'Horizontal Channel': {'symbol': '═', 'bias': 'neutral', 'strength': 0.5},
            
            # Rectangle Patterns
            'Rectangle': {'symbol': '▭', 'bias': 'neutral', 'strength': 0.5},
            'Rectangle Bullish': {'symbol': '▭', 'bias': 'bullish', 'strength': 0.7},
            'Rectangle Bearish': {'symbol': '▭', 'bias': 'bearish', 'strength': 0.7},
            
            # Flag and Pennant Patterns
            'Bull Flag': {'symbol': '⚑', 'bias': 'bullish', 'strength': 0.8},
            'Bear Flag': {'symbol': '⚐', 'bias': 'bearish', 'strength': 0.8},
            'Pennant': {'symbol': '⚐', 'bias': 'neutral', 'strength': 0.6},
            'Bull Pennant': {'symbol': '⚑', 'bias': 'bullish', 'strength': 0.75},
            'Bear Pennant': {'symbol': '⚐', 'bias': 'bearish', 'strength': 0.75},
            
            # Diamond Patterns
            'Diamond': {'symbol': '◈', 'bias': 'neutral', 'strength': 0.6},
            'Diamond Top': {'symbol': '◈', 'bias': 'bearish', 'strength': 0.75},
            'Diamond Bottom': {'symbol': '◈', 'bias': 'bullish', 'strength': 0.75},
            
            # Divergence Patterns
            'Bullish Divergence': {'symbol': '↗', 'bias': 'bullish', 'strength': 0.8},
            'Bearish Divergence': {'symbol': '↘', 'bias': 'bearish', 'strength': 0.8},
            'Hidden Bullish Divergence': {'symbol': '⤴', 'bias': 'bullish', 'strength': 0.7},
            'Hidden Bearish Divergence': {'symbol': '⤵', 'bias': 'bearish', 'strength': 0.7},
            
            # Harmonic Patterns
            'ABCD': {'symbol': 'A', 'bias': 'neutral', 'strength': 0.7},
            'AB=CD': {'symbol': '=', 'bias': 'neutral', 'strength': 0.65},
            'Gartley': {'symbol': 'G', 'bias': 'neutral', 'strength': 0.8},
            'Butterfly': {'symbol': 'B', 'bias': 'neutral', 'strength': 0.75},
            'Bat': {'symbol': 'b', 'bias': 'neutral', 'strength': 0.75},
            'Crab': {'symbol': 'C', 'bias': 'neutral', 'strength': 0.8},
            'Shark': {'symbol': 'S', 'bias': 'neutral', 'strength': 0.75},
            'Cypher': {'symbol': 'Y', 'bias': 'neutral', 'strength': 0.7},
            'Three Drives': {'symbol': '3', 'bias': 'neutral', 'strength': 0.7},
            
            # Support/Resistance
            'Support': {'symbol': '─', 'bias': 'bullish', 'strength': 0.6},
            'Resistance': {'symbol': '─', 'bias': 'bearish', 'strength': 0.6},
            'Support Break': {'symbol': '⚡', 'bias': 'bearish', 'strength': 0.8},
            'Resistance Break': {'symbol': '⚡', 'bias': 'bullish', 'strength': 0.8},
            
            # Gap Patterns
            'Breakaway Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.7},
            'Runaway Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.6},
            'Exhaustion Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.5},
            'Common Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.3},
            
            # Candlestick Patterns
            'Doji': {'symbol': '✚', 'bias': 'neutral', 'strength': 0.5},
            'Hammer': {'symbol': '🔨', 'bias': 'bullish', 'strength': 0.7},
            'Shooting Star': {'symbol': '☄', 'bias': 'bearish', 'strength': 0.7},
            'Engulfing Bull': {'symbol': '🟢', 'bias': 'bullish', 'strength': 0.75},
            'Engulfing Bear': {'symbol': '🔴', 'bias': 'bearish', 'strength': 0.75},
        }
        
        # Color scheme
        self.colors = {
            'bullish': Fore.GREEN,
            'bearish': Fore.RED,
            'neutral': Fore.YELLOW,
            'info': Fore.CYAN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'success': Fore.GREEN,
            'price': Fore.WHITE + Style.BRIGHT,
            'chart': Fore.BLUE,
            'pattern': Fore.MAGENTA,
            'confidence': Fore.CYAN
        }
    
    def log(self, level, message):
        """Colored logging with verbose control"""
        if not self.verbose and level in ['info', 'warning']:
            return
        
        color = self.colors.get(level, Fore.WHITE)
        prefix = {
            'info': '💡',
            'warning': '⚠️ ',
            'error': '❌',
            'success': '✅'
        }.get(level, '')
        
        print(f"{color}{prefix} {message}{Style.RESET_ALL}")
    
    def loading_animation(self, text, duration=2):
        """Loading animation with spinner"""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            print(f"\r{Fore.CYAN}{spinner[i % len(spinner)]} {text}...{Style.RESET_ALL}", end='', flush=True)
            time.sleep(0.1)
            i += 1
        
        # Clear the line and print completion
        print(f"\r{' ' * (len(text) + 20)}", end='')  # Clear the line
        print(f"\r{Fore.GREEN}✓ {text} complete{Style.RESET_ALL}")
        print()  # Add newline
    
    def calculate_time_bias(self, patterns, prices=None):
        """Calculate bias for different time horizons based on patterns"""
        if not patterns:
            return {'short': 'neutral', 'medium': 'neutral', 'long': 'neutral'}
        
        # Analyze patterns by type and confidence
        bullish_score = 0
        bearish_score = 0
        total_weight = 0
        
        for pattern in patterns:
            pattern_type = pattern.get('type', '')
            confidence = float(pattern.get('confidence', '50').rstrip('%')) / 100
            
            # Get pattern info
            pattern_info = self.patterns.get(pattern_type, {'bias': 'neutral', 'strength': 0.5})
            bias = pattern_info['bias']
            strength = pattern_info['strength']
            
            # Calculate weighted score
            weight = confidence * strength
            total_weight += weight
            
            if bias == 'bullish':
                bullish_score += weight
            elif bias == 'bearish':
                bearish_score += weight
        
        # Calculate net bias
        if total_weight == 0:
            net_bias = 0
        else:
            net_bias = (bullish_score - bearish_score) / total_weight
        
        def bias_to_text(bias_score):
            if bias_score > 0.15:  # More sensitive thresholds
                return 'bullish'
            elif bias_score < -0.15:
                return 'bearish'
            else:
                return 'neutral'
        
        # For different timeframes, apply different sensitivity
        short_bias = net_bias * 1.2  # More sensitive for short term
        medium_bias = net_bias * 1.0  # Normal sensitivity
        long_bias = net_bias * 0.8   # Less sensitive for long term
        
        return {
            'short': bias_to_text(short_bias),
            'medium': bias_to_text(medium_bias),
            'long': bias_to_text(long_bias)
        }
    
    def create_minimalist_chart(self, symbol, patterns, current_price, bias_analysis):
        """Create minimalist chart display"""
        # Calculate the maximum width needed
        max_width = 50
        
        # Create header
        header = f" {symbol} Analysis "
        header_padding = max_width - len(header)
        left_pad = header_padding // 2
        right_pad = header_padding - left_pad
        
        print(f"\n{Fore.WHITE + Style.BRIGHT}╭{'─' * left_pad}{header}{'─' * right_pad}╮{Style.RESET_ALL}")
        
        # Price display
        price_color = self.colors['price']
        price_text = f"${current_price:,.2f}"
        price_line = f"│ {price_color}{price_text:<{max_width-2}}{Style.RESET_ALL} │"
        print(price_line)
        
        # Time-based bias
        bias_colors = {
            'bullish': self.colors['bullish'] + '🟢',
            'bearish': self.colors['bearish'] + '🔴',
            'neutral': self.colors['neutral'] + '🟡'
        }
        
        # Bias lines with proper padding
        short_text = f"Short: {bias_analysis['short'].upper()}"
        medium_text = f"Medium: {bias_analysis['medium'].upper()}"
        long_text = f"Long: {bias_analysis['long'].upper()}"
        
        print(f"│ {Fore.CYAN}{short_text:<{max_width-2}}{Style.RESET_ALL} │")
        print(f"│ {Fore.CYAN}{medium_text:<{max_width-2}}{Style.RESET_ALL} │")
        print(f"│ {Fore.CYAN}{long_text:<{max_width-2}}{Style.RESET_ALL} │")
        
        # Separator
        print(f"│ {Fore.MAGENTA}{'Patterns:':<{max_width-2}}{Style.RESET_ALL} │")
        
        if patterns:
            # Sort by confidence and show top 5
            sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
            
            for i, pattern in enumerate(sorted_patterns[:5], 1):
                ptype = pattern.get('type', 'Unknown')
                confidence = pattern.get('confidence', '0%')
                
                pattern_info = self.patterns.get(ptype, {'symbol': '*', 'bias': 'neutral'})
                symbol_char = pattern_info['symbol']
                bias = pattern_info['bias']
                
                # Color code by bias
                bias_color = self.colors[bias]
                conf_value = float(confidence.rstrip('%'))
                
                # Confidence indicator
                if conf_value >= 80:
                    conf_indicator = '●'
                elif conf_value >= 60:
                    conf_indicator = '◐'
                elif conf_value >= 40:
                    conf_indicator = '◑'
                else:
                    conf_indicator = '○'
                
                # Truncate pattern name if too long
                pattern_name = ptype[:25] if len(ptype) > 25 else ptype
                pattern_text = f"{symbol_char} {pattern_name} {confidence} {conf_indicator}"
                
                print(f"│ {bias_color}{pattern_text:<{max_width-2}}{Style.RESET_ALL} │")
        else:
            no_patterns_text = "No patterns detected"
            print(f"│ {Fore.YELLOW}{no_patterns_text:<{max_width-2}}{Style.RESET_ALL} │")
        
        # Close the box
        print(f"{Fore.WHITE + Style.BRIGHT}╰{'─' * max_width}╯{Style.RESET_ALL}")
    
    def analyze_crypto(self, symbol, days=60, interval='1d'):
        """Analyze cryptocurrency with loading animation"""
        print(f"\n{Fore.CYAN + Style.BRIGHT}🚀 CryptVault Advanced Analysis{Style.RESET_ALL}")
        print(f"{Fore.WHITE}═" * 50 + Style.RESET_ALL)
        
        # Simple loading indicator
        print(f"{Fore.CYAN}⚡ Analyzing {symbol.upper()}...{Style.RESET_ALL}", end='', flush=True)
        
        try:
            # Perform analysis
            results = self.analyzer.analyze_ticker(symbol, days=days, interval=interval)
            
            # Clear loading line
            print(f"\r{' ' * 30}", end='')
            print(f"\r{Fore.GREEN}✓ Analysis complete{Style.RESET_ALL}")
            
            if not results['success']:
                self.log('error', f"Analysis failed: {results['error']}")
                return False
            
            # Extract data
            patterns = results.get('patterns', [])
            ticker_info = results.get('ticker_info', {})
            ml_predictions = results.get('ml_predictions', {})
            existing_chart = results.get('chart', '')
            
            current_price = ticker_info.get('current_price', 0)
            
            # Calculate time-based bias with enhanced analysis
            bias_analysis = self.calculate_time_bias(patterns)
            
            # Enhance bias with price momentum if available
            if ticker_info.get('price_change'):
                price_change = ticker_info['price_change']
                if 'percentage' in price_change:
                    change_pct = price_change['percentage']
                    if change_pct > 0.02:  # +2% or more
                        if bias_analysis['short'] == 'neutral':
                            bias_analysis['short'] = 'bullish'
                    elif change_pct < -0.02:  # -2% or more
                        if bias_analysis['short'] == 'neutral':
                            bias_analysis['short'] = 'bearish'
            
            # Display minimalist chart
            self.create_minimalist_chart(symbol.upper(), patterns, current_price, bias_analysis)
            
            # Always show chart (TradingView style)
            if existing_chart:
                print(f"\n{Fore.BLUE}📊 Chart Analysis:{Style.RESET_ALL}")
                print(existing_chart)
            else:
                # Try to create our own TradingView-style chart
                try:
                    # Fetch raw data for TradingView-style chart
                    from cryptvault.data.package_fetcher import PackageDataFetcher
                    data_fetcher = PackageDataFetcher()
                    raw_data = data_fetcher.get_data(symbol, days=days, interval=interval)
                    
                    if raw_data and len(raw_data.data) > 10:
                        tradingview_chart = self.create_tradingview_style_chart(raw_data, patterns, symbol)
                        print(f"\n{Fore.BLUE}📊 TradingView-Style Chart:{Style.RESET_ALL}")
                        print(tradingview_chart)
                except Exception as e:
                    self.log('warning', f"Could not create TradingView chart: {e}")
            
            # Show additional detailed analysis in verbose mode
            if self.verbose:
                self._show_detailed_analysis(patterns, ml_predictions)
            
            # Enhanced ML predictions
            ml_forecast = self.interpret_ml_predictions(ml_predictions, patterns, current_price)
            if ml_forecast:
                forecast_color = self.colors.get(ml_forecast['trend'].lower(), Fore.WHITE)
                print(f"\n{Fore.CYAN}🧠 ML Forecast:{Style.RESET_ALL} {forecast_color}{ml_forecast['trend'].upper()}{Style.RESET_ALL} ({ml_forecast['confidence']}% confidence)")
                
                if ml_forecast.get('target_price'):
                    print(f"{Fore.CYAN}🎯 Target Price:{Style.RESET_ALL} ${ml_forecast['target_price']:,.2f}")
            
            # Performance metrics
            analysis_time = results.get('analysis_time_seconds', 0)
            self.log('success', f"Analysis completed in {analysis_time:.2f}s | {len(patterns)} patterns found")
            
            return True
            
        except Exception as e:
            self.log('error', f"Analysis failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def analyze_multiple(self, symbols, days=60, interval='1d'):
        """Analyze multiple cryptocurrencies"""
        print(f"\n{Fore.CYAN + Style.BRIGHT}🎯 Multi-Asset Analysis{Style.RESET_ALL}")
        print(f"{Fore.WHITE}═" * 60 + Style.RESET_ALL)
        
        results = []
        for symbol in symbols:
            success = self.analyze_crypto(symbol, days, interval)
            results.append((symbol, success))
            
            if symbol != symbols[-1]:  # Not the last one
                print(f"\n{Fore.WHITE}─" * 50 + Style.RESET_ALL)
        
        # Summary
        successful = sum(1 for _, success in results if success)
        print(f"\n{Fore.CYAN}📊 Summary:{Style.RESET_ALL} {successful}/{len(symbols)} analyses completed")
        
        return results
    
    def interpret_ml_predictions(self, ml_predictions, patterns, current_price):
        """Interpret ML predictions and combine with pattern analysis"""
        if not ml_predictions:
            return None
        
        # Get base ML trend
        trend_forecast = ml_predictions.get('trend_forecast', {})
        base_trend = trend_forecast.get('trend_7d', 'sideways')
        base_strength = trend_forecast.get('trend_strength', '50.0%')
        
        # Parse strength percentage
        try:
            strength_value = float(base_strength.rstrip('%'))
        except:
            strength_value = 50.0
        
        # Combine with pattern analysis for enhanced prediction
        if patterns:
            bullish_patterns = 0
            bearish_patterns = 0
            total_confidence = 0
            
            for pattern in patterns:
                pattern_type = pattern.get('type', '')
                confidence = float(pattern.get('confidence', '50').rstrip('%'))
                pattern_info = self.patterns.get(pattern_type, {'bias': 'neutral'})
                
                if pattern_info['bias'] == 'bullish':
                    bullish_patterns += confidence
                elif pattern_info['bias'] == 'bearish':
                    bearish_patterns += confidence
                
                total_confidence += confidence
            
            # Adjust ML prediction based on patterns
            if total_confidence > 0:
                pattern_bias = (bullish_patterns - bearish_patterns) / total_confidence
                
                # Enhance the ML prediction
                if pattern_bias > 0.2 and base_trend == 'sideways':
                    enhanced_trend = 'bullish'
                    enhanced_strength = min(85, strength_value + abs(pattern_bias) * 30)
                elif pattern_bias < -0.2 and base_trend == 'sideways':
                    enhanced_trend = 'bearish'
                    enhanced_strength = min(85, strength_value + abs(pattern_bias) * 30)
                elif pattern_bias > 0.1 and base_trend == 'bearish':
                    enhanced_trend = 'neutral'
                    enhanced_strength = 60
                elif pattern_bias < -0.1 and base_trend == 'bullish':
                    enhanced_trend = 'neutral'
                    enhanced_strength = 60
                else:
                    enhanced_trend = base_trend
                    enhanced_strength = strength_value
            else:
                enhanced_trend = base_trend
                enhanced_strength = strength_value
        else:
            enhanced_trend = base_trend
            enhanced_strength = strength_value
        
        # Calculate target price based on trend
        target_price = None
        if enhanced_trend == 'bullish':
            target_price = current_price * (1 + (enhanced_strength / 100) * 0.1)  # Up to 10% move
        elif enhanced_trend == 'bearish':
            target_price = current_price * (1 - (enhanced_strength / 100) * 0.1)  # Down to 10% move
        
        return {
            'trend': enhanced_trend,
            'confidence': int(enhanced_strength),
            'target_price': target_price
        }
    
    def _show_detailed_analysis(self, patterns, ml_predictions):
        """Show detailed analysis in verbose mode"""
        print(f"\n{Fore.CYAN}📈 Detailed Pattern Analysis:{Style.RESET_ALL}")
        
        if patterns:
            # Group patterns by type
            pattern_groups = {}
            for pattern in patterns:
                ptype = pattern.get('type', 'Unknown')
                if ptype not in pattern_groups:
                    pattern_groups[ptype] = []
                pattern_groups[ptype].append(pattern)
            
            # Show pattern details
            for ptype, group in pattern_groups.items():
                pattern_info = self.patterns.get(ptype, {'symbol': '*', 'bias': 'neutral'})
                symbol = pattern_info['symbol']
                bias_color = self.colors[pattern_info['bias']]
                
                print(f"  {bias_color}{symbol} {ptype}:{Style.RESET_ALL}")
                for pattern in group:
                    confidence = pattern.get('confidence', '0%')
                    if 'target_price' in pattern:
                        print(f"    Target: ${pattern['target_price']:.2f} | Confidence: {confidence}")
                    if 'description' in pattern:
                        desc = pattern['description'][:60] + "..." if len(pattern['description']) > 60 else pattern['description']
                        print(f"    {desc}")
        
        # ML model details
        if ml_predictions:
            print(f"\n{Fore.CYAN}🤖 ML Model Details:{Style.RESET_ALL}")
            if 'ensemble_accuracy' in ml_predictions:
                accuracy = ml_predictions['ensemble_accuracy']
                print(f"  Ensemble Accuracy: {accuracy:.1%}")
            
            if 'model_weights' in ml_predictions:
                weights = ml_predictions['model_weights']
                print(f"  Active Models:")
                for model, weight in weights.items():
                    if weight > 0.01:
                        print(f"    {model}: {weight:.1%}")
    
    def create_tradingview_style_chart(self, data, patterns, symbol, width=80, height=25):
        """Create TradingView-style ASCII chart with candlesticks and indicators"""
        if not data or len(data.data) < 2:
            return "Insufficient data for TradingView-style chart"
        
        # Extract OHLCV data
        data_points = data.data
        opens = [point.open for point in data_points]
        highs = [point.high for point in data_points]
        lows = [point.low for point in data_points]
        closes = [point.close for point in data_points]
        volumes = [point.volume for point in data_points]
        dates = [point.timestamp for point in data_points]
        
        # Calculate price range
        all_prices = opens + highs + lows + closes
        min_price = min(all_prices)
        max_price = max(all_prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = max_price * 0.01
        
        # Create chart grid
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw candlesticks (TradingView style)
        for i in range(len(data_points)):
            x = int((i / (len(data_points) - 1)) * (width - 1))
            
            # Calculate y positions
            open_y = int(((opens[i] - min_price) / price_range) * (height - 1))
            high_y = int(((highs[i] - min_price) / price_range) * (height - 1))
            low_y = int(((lows[i] - min_price) / price_range) * (height - 1))
            close_y = int(((closes[i] - min_price) / price_range) * (height - 1))
            
            # Ensure coordinates are within bounds
            open_y = max(0, min(height - 1, open_y))
            high_y = max(0, min(height - 1, high_y))
            low_y = max(0, min(height - 1, low_y))
            close_y = max(0, min(height - 1, close_y))
            x = max(0, min(width - 1, x))
            
            # Draw high-low line (wick)
            for y in range(min(low_y, high_y), max(low_y, high_y) + 1):
                if 0 <= y < height:
                    chart[height - 1 - y][x] = '│'
            
            # Draw body
            body_start = min(open_y, close_y)
            body_end = max(open_y, close_y)
            
            # Determine candle color and character
            if closes[i] >= opens[i]:  # Bullish candle
                body_char = '█' if body_end > body_start else '─'
                color_indicator = '🟢' if i == len(data_points) - 1 else ''
            else:  # Bearish candle
                body_char = '▓' if body_end > body_start else '─'
                color_indicator = '🔴' if i == len(data_points) - 1 else ''
            
            # Draw candle body
            if body_end > body_start:
                for y in range(body_start, body_end + 1):
                    if 0 <= y < height:
                        chart[height - 1 - y][x] = body_char
            else:
                # Doji or very small body
                if 0 <= body_start < height:
                    chart[height - 1 - body_start][x] = '─'
        
        # Add pattern overlays (TradingView style)
        self._add_tradingview_patterns(chart, patterns, width, height, min_price, price_range)
        
        # Add technical indicators
        self._add_technical_indicators(chart, closes, width, height, min_price, price_range)
        
        # Convert chart to string with TradingView styling
        chart_lines = []
        
        # Add title
        chart_lines.append(f"{Fore.WHITE + Style.BRIGHT}{'═' * (width + 10)}{Style.RESET_ALL}")
        chart_lines.append(f"{Fore.WHITE + Style.BRIGHT}  📊 {symbol} - TradingView Style Chart{Style.RESET_ALL}")
        chart_lines.append(f"{Fore.WHITE + Style.BRIGHT}{'═' * (width + 10)}{Style.RESET_ALL}")
        
        # Add price labels and chart
        for i, row in enumerate(chart):
            price_at_row = min_price + (price_range * (height - 1 - i) / (height - 1))
            price_label = f"{price_at_row:8.2f}"
            
            # Color code the price labels
            if i == 0:  # Highest price
                price_color = Fore.GREEN
            elif i == height - 1:  # Lowest price
                price_color = Fore.RED
            else:
                price_color = Fore.WHITE
            
            chart_lines.append(f"{price_color}{price_label}{Style.RESET_ALL} │{''.join(row)}│")
        
        # Add bottom border
        chart_lines.append(f"         └{'─' * width}┘")
        
        # Add date labels
        start_date = dates[0].strftime("%m/%d") if dates else "Start"
        end_date = dates[-1].strftime("%m/%d") if dates else "End"
        date_line = f"          {start_date}{' ' * (width - len(start_date) - len(end_date))}{end_date}"
        chart_lines.append(date_line)
        
        # Add volume bars (TradingView style)
        if volumes:
            chart_lines.append("")
            chart_lines.append(f"{Fore.CYAN}📊 Volume Profile:{Style.RESET_ALL}")
            
            max_volume = max(volumes) if volumes else 1
            volume_bar_width = 30
            
            # Show last 5 volume bars
            for i in range(max(0, len(volumes) - 5), len(volumes)):
                vol_ratio = volumes[i] / max_volume if max_volume > 0 else 0
                bar_length = int(vol_ratio * volume_bar_width)
                
                # Color code volume bars
                if i > 0 and closes[i] >= closes[i-1]:
                    vol_color = Fore.GREEN
                else:
                    vol_color = Fore.RED
                
                volume_bar = '█' * bar_length + '░' * (volume_bar_width - bar_length)
                date_str = dates[i].strftime("%m/%d") if i < len(dates) else f"#{i+1}"
                
                chart_lines.append(f"  {date_str}: {vol_color}{volume_bar}{Style.RESET_ALL} {volumes[i]:,.0f}")
        
        # Add current price and change
        if len(closes) >= 2:
            current_price = closes[-1]
            prev_price = closes[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
            
            change_color = Fore.GREEN if change >= 0 else Fore.RED
            change_symbol = "▲" if change >= 0 else "▼"
            
            chart_lines.append("")
            chart_lines.append(f"{Fore.WHITE + Style.BRIGHT}💰 Current: ${current_price:,.2f} {change_color}{change_symbol} ${abs(change):.2f} ({change_pct:+.2f}%){Style.RESET_ALL}")
        
        # Add technical analysis summary
        if len(closes) >= 20:
            ma20 = sum(closes[-20:]) / 20
            ma_trend = "Above MA20" if current_price > ma20 else "Below MA20"
            ma_color = Fore.GREEN if current_price > ma20 else Fore.RED
            
            chart_lines.append(f"{Fore.CYAN}📈 MA20: ${ma20:.2f} | Price is {ma_color}{ma_trend}{Style.RESET_ALL}")
        
        # Add pattern legend
        if patterns:
            chart_lines.append("")
            chart_lines.append(f"{Fore.MAGENTA}🎯 Pattern Legend:{Style.RESET_ALL}")
            
            pattern_legend = []
            for pattern in patterns[:3]:  # Top 3 patterns
                ptype = pattern.get('type', 'Unknown')
                pattern_info = self.patterns.get(ptype, {'symbol': '*', 'bias': 'neutral'})
                symbol = pattern_info['symbol']
                bias_color = self.colors[pattern_info['bias']]
                confidence = pattern.get('confidence', '0%')
                
                pattern_legend.append(f"{bias_color}{symbol} {ptype} ({confidence}){Style.RESET_ALL}")
            
            chart_lines.append("  " + " | ".join(pattern_legend))
        
        return '\n'.join(chart_lines)
    
    def _add_tradingview_patterns(self, chart, patterns, width, height, min_price, price_range):
        """Add TradingView-style pattern overlays"""
        if not patterns:
            return
        
        # Sort patterns by confidence
        sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
        
        for i, pattern in enumerate(sorted_patterns[:5]):  # Top 5 patterns
            pattern_type = pattern.get('type', 'Unknown')
            pattern_info = self.patterns.get(pattern_type, {'symbol': '*', 'bias': 'neutral'})
            symbol = pattern_info['symbol']
            
            # Place pattern markers at different positions
            if 'start_index' in pattern and 'end_index' in pattern:
                start_idx = max(0, min(pattern['start_index'], width - 1))
                end_idx = max(0, min(pattern['end_index'], width - 1))
                
                # Draw pattern boundary
                marker_y = height // 4 + (i % 3)
                marker_y = max(0, min(height - 1, marker_y))
                
                # Draw pattern line
                for x in range(start_idx, min(end_idx + 1, width)):
                    if chart[marker_y][x] == ' ':
                        if x == start_idx:
                            chart[marker_y][x] = symbol
                        elif x == end_idx:
                            confidence = float(pattern.get('confidence', '0').rstrip('%'))
                            if confidence >= 80:
                                chart[marker_y][x] = '●'
                            elif confidence >= 60:
                                chart[marker_y][x] = '◐'
                            else:
                                chart[marker_y][x] = '○'
                        elif (x - start_idx) % 3 == 0:
                            chart[marker_y][x] = '┈'
    
    def _add_technical_indicators(self, chart, prices, width, height, min_price, price_range):
        """Add technical indicators like moving averages"""
        if len(prices) < 20:
            return
        
        # Calculate 20-period moving average
        ma20 = []
        for i in range(len(prices)):
            if i >= 19:
                ma_value = sum(prices[i-19:i+1]) / 20
                ma20.append(ma_value)
            else:
                ma20.append(prices[i])
        
        # Plot MA20 line
        for i in range(1, len(ma20)):
            x1 = int(((i-1) / (len(ma20) - 1)) * (width - 1))
            x2 = int((i / (len(ma20) - 1)) * (width - 1))
            
            y1 = int(((ma20[i-1] - min_price) / price_range) * (height - 1))
            y2 = int(((ma20[i] - min_price) / price_range) * (height - 1))
            
            # Ensure coordinates are within bounds
            y1 = max(0, min(height - 1, y1))
            y2 = max(0, min(height - 1, y2))
            x1 = max(0, min(width - 1, x1))
            x2 = max(0, min(width - 1, x2))
            
            # Draw MA line
            if x1 != x2:
                steps = abs(x2 - x1)
                for step in range(steps + 1):
                    x = x1 + int((x2 - x1) * step / steps) if steps > 0 else x1
                    y = y1 + int((y2 - y1) * step / steps) if steps > 0 else y1
                    
                    if 0 <= x < width and 0 <= y < height:
                        if chart[height - 1 - y][x] == ' ':
                            chart[height - 1 - y][x] = '·'  # MA20 indicator

def main():
    """Main function with enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description="Advanced CryptVault Terminal Charts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced_crypto_charts.py BTC              # Quick Bitcoin analysis
  python advanced_crypto_charts.py ETH 30 4h       # Ethereum 30 days, 4h intervals
  python advanced_crypto_charts.py -m BTC ETH ADA  # Multi-asset analysis
  python advanced_crypto_charts.py BTC -v          # Verbose mode with detailed charts
        """
    )
    
    parser.add_argument('symbol', nargs='?', default='BTC', help='Cryptocurrency symbol')
    parser.add_argument('days', nargs='?', type=int, default=60, help='Number of days (default: 60)')
    parser.add_argument('interval', nargs='?', default='1d', help='Data interval (default: 1d)')
    parser.add_argument('-m', '--multiple', nargs='+', help='Analyze multiple symbols')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output with detailed charts')
    parser.add_argument('--quick', action='store_true', help='Quick analysis mode')
    
    args = parser.parse_args()
    
    # Initialize charts
    charts = AdvancedCryptoCharts(verbose=args.verbose)
    
    try:
        if args.multiple:
            # Multi-asset analysis
            charts.analyze_multiple(args.multiple, args.days, args.interval)
        else:
            # Single asset analysis
            charts.analyze_crypto(args.symbol, args.days, args.interval)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Analysis interrupted{Style.RESET_ALL}")
    except Exception as e:
        charts.log('error', f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()